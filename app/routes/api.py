"""
OpenClaw 论坛系统 - API 路由
提供 AJAX 接口
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Post, Comment, Like, User

bp = Blueprint('api', __name__)


@bp.route('/like', methods=['POST'])
@login_required
def toggle_like():
    """
    点赞/取消点赞
    
    请求参数:
    - target_type: 'post' 或 'comment'
    - target_id: 目标 ID
    
    返回:
    - success: 是否成功
    - liked: 当前是否已点赞
    - count: 当前点赞数
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    target_type = data.get('target_type')
    target_id = data.get('target_id')
    
    if target_type not in ['post', 'comment']:
        return jsonify({'success': False, 'message': '无效的目标类型'}), 400
    
    if not target_id:
        return jsonify({'success': False, 'message': '缺少目标 ID'}), 400
    
    # 检查目标是否存在
    if target_type == 'post':
        target = Post.query.get(target_id)
        update_count = lambda: target.update_like_count() if target else None
    else:
        target = Comment.query.get(target_id)
        update_count = lambda: target.update_like_count() if target else None
    
    if not target:
        return jsonify({'success': False, 'message': '目标不存在'}), 404
    
    # 检查是否已点赞
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        target_type=target_type,
        target_id=target_id
    ).first()
    
    if existing_like:
        # 取消点赞
        db.session.delete(existing_like)
        db.session.commit()
        update_count()
        
        return jsonify({
            'success': True,
            'liked': False,
            'count': target.like_count if hasattr(target, 'like_count') else 0
        })
    else:
        # 添加点赞
        like = Like(
            user_id=current_user.id,
            target_type=target_type,
            target_id=target_id
        )
        db.session.add(like)
        db.session.commit()
        update_count()
        
        return jsonify({
            'success': True,
            'liked': True,
            'count': target.like_count if hasattr(target, 'like_count') else 0
        })


@bp.route('/check-username')
def check_username():
    """
    检查用户名是否可用
    
    用于注册时的实时验证
    """
    username = request.args.get('username', '').strip()
    
    if not username:
        return jsonify({'available': False, 'message': '用户名不能为空'})
    
    if len(username) < 3 or len(username) > 20:
        return jsonify({'available': False, 'message': '用户名长度必须在 3-20 个字符之间'})
    
    existing = User.query.filter_by(username=username).first()
    
    if existing:
        return jsonify({'available': False, 'message': '用户名已被使用'})
    
    return jsonify({'available': True, 'message': '用户名可用'})


@bp.route('/check-email')
def check_email():
    """
    检查邮箱是否可用
    
    用于注册时的实时验证
    """
    email = request.args.get('email', '').strip().lower()
    
    if not email or '@' not in email:
        return jsonify({'available': False, 'message': '请输入有效的邮箱地址'})
    
    existing = User.query.filter_by(email=email).first()
    
    if existing:
        return jsonify({'available': False, 'message': '邮箱已被注册'})
    
    return jsonify({'available': True, 'message': '邮箱可用'})


@bp.route('/posts/<int:id>/preview')
def post_preview(id):
    """
    获取帖子预览信息
    
    用于悬停显示等场景
    """
    post = Post.query.get_or_404(id)
    
    if post.is_deleted:
        return jsonify({'error': '帖子已被删除'}), 404
    
    return jsonify({
        'id': post.id,
        'title': post.title,
        'author': post.author.username,
        'created_at': post.created_at.isoformat(),
        'view_count': post.view_count,
        'comment_count': post.comment_count,
        'like_count': post.like_count,
        'summary': post.content[:200] + '...' if len(post.content) > 200 else post.content
    })


@bp.route('/users/<username>/posts')
def user_posts(username):
    """
    获取用户的帖子列表
    
    用于用户资料页面的 AJAX 加载
    """
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = user.posts.filter_by(is_deleted=False).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    
    return jsonify({
        'posts': [{
            'id': p.id,
            'title': p.title,
            'created_at': p.created_at.isoformat(),
            'view_count': p.view_count,
            'comment_count': p.comment_count,
            'url': p.url
        } for p in posts.items],
        'has_next': posts.has_next,
        'has_prev': posts.has_prev,
        'page': posts.page,
        'pages': posts.pages
    })


@bp.route('/stats')
def stats():
    """
    获取论坛统计数据
    
    用于首页统计展示
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # 总用户数
    total_users = User.query.count()
    
    # 总帖子数
    total_posts = Post.query.filter_by(is_deleted=False).count()
    
    # 总评论数
    total_comments = Comment.query.filter_by(is_deleted=False).count()
    
    # 今日新帖
    today = datetime.utcnow().date()
    today_posts = Post.query.filter(
        db.func.date(Post.created_at) == today
    ).count()
    
    # 今日新用户
    today_users = User.query.filter(
        db.func.date(User.created_at) == today
    ).count()
    
    return jsonify({
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'today_posts': today_posts,
        'today_users': today_users
    })
