"""
OpenClaw 论坛系统 - 论坛主路由
处理帖子列表、详情、发布、编辑等功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, func
from app import db
from app.models import Post, Category, Tag, Comment, Like, User
from app.utils import paginate
from app.content_moderation import moderate_post, moderate_comment

bp = Blueprint('forum', __name__)


@bp.route('/')
def index():
    """首页 - 帖子列表"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    tag_name = request.args.get('tag')
    sort = request.args.get('sort', 'latest')  # latest, hot, top
    
    # 基础查询
    query = Post.query.filter_by(is_deleted=False)
    
    # 分类筛选
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # 标签筛选
    if tag_name:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            query = query.filter(Post.tags.contains(tag))
    
    # 排序
    if sort == 'hot':
        query = query.order_by(Post.view_count.desc(), Post.created_at.desc())
    elif sort == 'top':
        query = query.order_by(Post.like_count.desc(), Post.created_at.desc())
    else:  # latest
        query = query.order_by(Post.is_pinned.desc(), Post.created_at.desc())
    
    # 分页
    posts = query.paginate(page=page, per_page=10, error_out=False)
    
    return render_template('forum/index.html', 
                         posts=posts, 
                         category_id=category_id,
                         tag_name=tag_name,
                         sort=sort)


@bp.route('/post/<int:id>')
def post_detail(id):
    """帖子详情页"""
    post = Post.query.get_or_404(id)
    
    if post.is_deleted and not (current_user.is_authenticated and current_user.is_admin):
        flash('该帖子已被删除', 'warning')
        return redirect(url_for('forum.index'))
    
    # 增加浏览量
    post.increment_view()
    
    # 获取评论
    page = request.args.get('page', 1, type=int)
    comments = post.comments.filter_by(is_deleted=False, parent_id=None).order_by(
        Comment.created_at.asc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    # 检查当前用户是否已点赞
    has_liked = False
    if current_user.is_authenticated:
        has_liked = current_user.has_liked('post', post.id)
    
    # 获取相关帖子（同分类，排除当前帖子）
    related_posts = Post.query.filter_by(
        category_id=post.category_id, 
        is_deleted=False
    ).filter(
        Post.id != post.id
    ).order_by(
        Post.created_at.desc()
    ).limit(5).all()
    
    return render_template('forum/post_detail.html', 
                         post=post, 
                         comments=comments,
                         has_liked=has_liked,
                         related_posts=related_posts)


@bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """创建新帖子"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category_id = request.form.get('category', type=int)
        tag_names = request.form.get('tags', '').strip()
        
        # 验证
        errors = []
        
        if not title or len(title) < 5:
            errors.append('标题至少需要 5 个字符')
        
        if len(title) > 200:
            errors.append('标题不能超过 200 个字符')
        
        if not content or len(content) < 10:
            errors.append('内容至少需要 10 个字符')
        
        if not category_id:
            errors.append('请选择分类')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('forum/create_post.html',
                                 title=title, content=content,
                                 category_id=category_id, tags=tag_names)
        
        # 内容审核
        moderation_result = moderate_post(title, content)
        if moderation_result.is_violation:
            # 创建被标记为删除的帖子（仅管理员可见）
            post = Post(
                title=title,
                content=f"[内容审核未通过: {moderation_result.reason}]\n\n{content}",
                author_id=current_user.id,
                category_id=category_id,
                is_deleted=True  # 自动标记为删除
            )
            db.session.add(post)
            db.session.commit()
            
            flash(f'帖子内容违规: {moderation_result.reason}。帖子已被隐藏，请联系管理员。', 'danger')
            return redirect(url_for('forum.index'))
        
        # 创建帖子
        post = Post(
            title=title,
            content=content,
            author_id=current_user.id,
            category_id=category_id
        )
        
        # 处理标签
        if tag_names:
            tag_list = [t.strip() for t in tag_names.split(',') if t.strip()]
            for tag_name in tag_list[:5]:  # 最多 5 个标签
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        
        # 更新计数
        current_user.update_post_count()
        post.category.update_post_count()
        
        flash('帖子发布成功！', 'success')
        return redirect(url_for('forum.post_detail', id=post.id))
    
    return render_template('forum/create_post.html')


@bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """编辑帖子"""
    post = Post.query.get_or_404(id)
    
    # 检查权限
    if post.author_id != current_user.id and not current_user.is_admin:
        flash('您没有权限编辑此帖子', 'danger')
        return redirect(url_for('forum.post_detail', id=id))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category_id = request.form.get('category', type=int)
        tag_names = request.form.get('tags', '').strip()
        
        # 验证
        if not title or len(title) < 5:
            flash('标题至少需要 5 个字符', 'danger')
            return render_template('forum/edit_post.html', post=post)
        
        if not content or len(content) < 10:
            flash('内容至少需要 10 个字符', 'danger')
            return render_template('forum/edit_post.html', post=post)
        
        # 更新帖子
        old_category_id = post.category_id
        
        post.title = title
        post.content = content
        post.category_id = category_id
        
        # 更新标签
        post.tags = []
        if tag_names:
            tag_list = [t.strip() for t in tag_names.split(',') if t.strip()]
            for tag_name in tag_list[:5]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        
        db.session.commit()
        
        # 更新分类计数
        if old_category_id != category_id:
            Category.query.get(old_category_id).update_post_count()
            post.category.update_post_count()
        
        flash('帖子更新成功！', 'success')
        return redirect(url_for('forum.post_detail', id=post.id))
    
    return render_template('forum/edit_post.html', post=post)


@bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    """删除帖子（软删除）"""
    post = Post.query.get_or_404(id)
    
    # 检查权限
    if post.author_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此帖子', 'danger')
        return redirect(url_for('forum.post_detail', id=id))
    
    post.soft_delete()
    flash('帖子已删除', 'success')
    return redirect(url_for('forum.index'))


@bp.route('/post/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    """添加评论"""
    post = Post.query.get_or_404(id)
    
    if post.is_locked:
        flash('该帖子已锁定，无法评论', 'warning')
        return redirect(url_for('forum.post_detail', id=id))
    
    content = request.form.get('content', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    
    if not content or len(content) < 2:
        flash('评论内容太短', 'danger')
        return redirect(url_for('forum.post_detail', id=id))
    
    # 内容审核
    moderation_result = moderate_comment(content)
    if moderation_result.is_violation:
        flash(f'评论内容违规: {moderation_result.reason}，请修改后重试。', 'danger')
        return redirect(url_for('forum.post_detail', id=id))
    
    comment = Comment(
        content=content,
        author_id=current_user.id,
        post_id=post.id,
        parent_id=parent_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # 更新计数
    post.update_comment_count()
    current_user.update_comment_count()
    
    flash('评论发布成功', 'success')
    return redirect(url_for('forum.post_detail', id=id, _anchor=f'comment-{comment.id}'))


@bp.route('/comment/<int:id>/delete', methods=['POST'])
@login_required
def delete_comment(id):
    """删除评论"""
    comment = Comment.query.get_or_404(id)
    
    # 检查权限
    if comment.author_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此评论', 'danger')
        return redirect(url_for('forum.post_detail', id=comment.post_id))
    
    comment.soft_delete()
    flash('评论已删除', 'success')
    return redirect(url_for('forum.post_detail', id=comment.post_id))


@bp.route('/search')
def search():
    """搜索功能"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if not query or len(query) < 2:
        flash('搜索关键词至少需要 2 个字符', 'warning')
        return render_template('forum/search.html', query=query, posts=None)
    
    # 搜索帖子标题和内容
    posts = Post.query.filter(
        Post.is_deleted == False,
        or_(
            Post.title.contains(query),
            Post.content.contains(query)
        )
    ).order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('forum/search.html', query=query, posts=posts)


@bp.route('/tags')
def tags():
    """标签云页面"""
    # 获取所有标签，按帖子数排序
    all_tags = Tag.query.order_by(Tag.post_count.desc()).all()
    return render_template('forum/tags.html', tags=all_tags)
