"""
OpenClaw 论坛系统 - 管理后台路由
处理管理员功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Post, Comment, Category, Tag, Setting

bp = Blueprint('admin', __name__)


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('您没有权限访问此页面', 'danger')
            return redirect(url_for('forum.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
@admin_required
def dashboard():
    """管理后台首页"""
    # 统计数据
    stats = {
        'user_count': User.query.count(),
        'post_count': Post.query.filter_by(is_deleted=False).count(),
        'comment_count': Comment.query.filter_by(is_deleted=False).count(),
        'today_posts': Post.query.filter(
            db.func.date(Post.created_at) == db.func.current_date()
        ).count(),
    }
    
    # 最新用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # 最新帖子
    recent_posts = Post.query.filter_by(is_deleted=False).order_by(
        Post.created_at.desc()
    ).limit(5).all()
    
    # 待审核内容（如果有审核功能）
    # pending_posts = Post.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         recent_posts=recent_posts)


# ==================== 用户管理 ====================

@bp.route('/users')
@login_required
@admin_required
def users():
    """用户列表"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, search=search)


@bp.route('/users/<int:id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(id):
    """切换用户管理员状态"""
    user = User.query.get_or_404(id)
    
    # 不能取消自己的管理员权限
    if user.id == current_user.id:
        flash('不能修改自己的管理员状态', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = '设为管理员' if user.is_admin else '取消管理员'
    flash(f'用户 {user.username} 已{status}', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_active(id):
    """切换用户激活状态"""
    user = User.query.get_or_404(id)
    
    # 不能禁用自己的账号
    if user.id == current_user.id:
        flash('不能禁用自己的账号', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = '激活' if user.is_active else '禁用'
    flash(f'用户 {user.username} 已{status}', 'success')
    return redirect(url_for('admin.users'))


@bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """删除用户"""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('不能删除自己的账号', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'用户 {username} 已删除', 'success')
    return redirect(url_for('admin.users'))


# ==================== 帖子管理 ====================

@bp.route('/posts')
@login_required
@admin_required
def posts():
    """帖子管理"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')  # all, deleted, pinned
    
    query = Post.query
    
    if status == 'deleted':
        query = query.filter_by(is_deleted=True)
    elif status == 'active':
        query = query.filter_by(is_deleted=False)
    
    posts = query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/posts.html', posts=posts, status=status)


@bp.route('/posts/<int:id>/toggle-pin', methods=['POST'])
@login_required
@admin_required
def toggle_pin(id):
    """切换帖子置顶状态"""
    post = Post.query.get_or_404(id)
    post.is_pinned = not post.is_pinned
    db.session.commit()
    
    status = '置顶' if post.is_pinned else '取消置顶'
    flash(f'帖子已{status}', 'success')
    return redirect(url_for('admin.posts'))


@bp.route('/posts/<int:id>/toggle-lock', methods=['POST'])
@login_required
@admin_required
def toggle_lock(id):
    """切换帖子锁定状态"""
    post = Post.query.get_or_404(id)
    post.is_locked = not post.is_locked
    db.session.commit()
    
    status = '锁定' if post.is_locked else '解锁'
    flash(f'帖子已{status}', 'success')
    return redirect(url_for('admin.posts'))


@bp.route('/posts/<int:id>/restore', methods=['POST'])
@login_required
@admin_required
def restore_post(id):
    """恢复已删除的帖子"""
    post = Post.query.get_or_404(id)
    post.restore()
    flash('帖子已恢复', 'success')
    return redirect(url_for('admin.posts'))


@bp.route('/posts/<int:id>/hard-delete', methods=['POST'])
@login_required
@admin_required
def hard_delete_post(id):
    """永久删除帖子"""
    post = Post.query.get_or_404(id)
    
    # 硬删除
    db.session.delete(post)
    db.session.commit()
    
    flash('帖子已永久删除', 'success')
    return redirect(url_for('admin.posts'))


# ==================== 评论管理 ====================

@bp.route('/comments')
@login_required
@admin_required
def comments():
    """评论管理"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Comment.query
    
    if status == 'deleted':
        query = query.filter_by(is_deleted=True)
    elif status == 'active':
        query = query.filter_by(is_deleted=False)
    
    comments = query.order_by(Comment.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/comments.html', comments=comments, status=status)


# ==================== 分类管理 ====================

@bp.route('/categories')
@login_required
@admin_required
def categories():
    """分类管理"""
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)


@bp.route('/categories/create', methods=['POST'])
@login_required
@admin_required
def create_category():
    """创建分类"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    sort_order = request.form.get('sort_order', 0, type=int)
    
    if not name:
        flash('分类名称不能为空', 'danger')
        return redirect(url_for('admin.categories'))
    
    if Category.query.filter_by(name=name).first():
        flash('分类名称已存在', 'danger')
        return redirect(url_for('admin.categories'))
    
    category = Category(
        name=name,
        description=description,
        sort_order=sort_order
    )
    db.session.add(category)
    db.session.commit()
    
    flash('分类创建成功', 'success')
    return redirect(url_for('admin.categories'))


@bp.route('/categories/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_category(id):
    """编辑分类"""
    category = Category.query.get_or_404(id)
    
    category.name = request.form.get('name', '').strip()
    category.description = request.form.get('description', '').strip()
    category.sort_order = request.form.get('sort_order', 0, type=int)
    category.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash('分类更新成功', 'success')
    return redirect(url_for('admin.categories'))


@bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    """删除分类"""
    category = Category.query.get_or_404(id)
    
    # 检查是否有帖子使用此分类
    if category.post_count > 0:
        flash('该分类下还有帖子，无法删除', 'danger')
        return redirect(url_for('admin.categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('分类已删除', 'success')
    return redirect(url_for('admin.categories'))


# ==================== 标签管理 ====================

@bp.route('/tags')
@login_required
@admin_required
def admin_tags():
    """标签管理"""
    page = request.args.get('page', 1, type=int)
    tags = Tag.query.order_by(Tag.post_count.desc()).paginate(
        page=page, per_page=30, error_out=False
    )
    return render_template('admin/tags.html', tags=tags)


@bp.route('/tags/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_tag(id):
    """编辑标签"""
    tag = Tag.query.get_or_404(id)
    
    new_name = request.form.get('name', '').strip()
    
    if new_name and new_name != tag.name:
        # 检查名称是否已存在
        if Tag.query.filter_by(name=new_name).first():
            flash('标签名称已存在', 'danger')
        else:
            tag.name = new_name
            db.session.commit()
            flash('标签更新成功', 'success')
    
    return redirect(url_for('admin.admin_tags'))


@bp.route('/tags/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tag(id):
    """删除标签"""
    tag = Tag.query.get_or_404(id)
    
    db.session.delete(tag)
    db.session.commit()
    
    flash('标签已删除', 'success')
    return redirect(url_for('admin.admin_tags'))


# ==================== 系统设置 ====================

@bp.route('/settings')
@login_required
@admin_required
def settings():
    """系统设置"""
    return render_template('admin/settings.html')
