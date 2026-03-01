"""
模型单元测试
"""
import pytest
from app.models import User, Post, Comment, Category, Tag, Like, Notification


def test_user_creation(app):
    """测试用户创建"""
    with app.app_context():
        user = User(username='test', email='test@test.com')
        user.set_password('password')
        assert user.username == 'test'
        assert user.check_password('password') is True
        assert user.check_password('wrong') is False


def test_user_password_hashing(app):
    """测试密码哈希"""
    with app.app_context():
        user = User(username='test', email='test@test.com')
        user.set_password('mypassword')
        assert user.password_hash != 'mypassword'
        assert user.check_password('mypassword') is True


def test_post_creation(app, init_data):
    """测试帖子创建"""
    with app.app_context():
        from app import db
        post = Post(
            title='测试标题',
            content='测试内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        db.session.add(post)
        db.session.commit()
        
        assert post.id is not None
        assert post.title == '测试标题'
        assert post.author.username == 'testuser'


def test_comment_creation(app, init_data):
    """测试评论创建"""
    with app.app_context():
        from app import db
        post = Post(
            title='测试帖子',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        db.session.add(post)
        db.session.commit()
        
        comment = Comment(
            content='测试评论',
            author_id=init_data['user'].id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        
        assert comment.id is not None
        assert comment.post.title == '测试帖子'


def test_category_post_count(app, init_data):
    """测试分类帖子计数"""
    with app.app_context():
        from app import db
        initial_count = init_data['category'].post_count
        
        post = Post(
            title='新帖子',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        db.session.add(post)
        db.session.commit()
        
        init_data['category'].update_post_count()
        assert init_data['category'].post_count == initial_count + 1


def test_like_creation(app, init_data):
    """测试点赞创建"""
    with app.app_context():
        from app import db
        post = Post(
            title='测试帖子',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        db.session.add(post)
        db.session.commit()
        
        like = Like(
            user_id=init_data['user'].id,
            target_type='post',
            target_id=post.id
        )
        db.session.add(like)
        db.session.commit()
        
        assert like.id is not None


def test_user_has_liked(app, init_data):
    """测试用户点赞检查"""
    with app.app_context():
        from app import db
        post = Post(
            title='测试帖子',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        db.session.add(post)
        db.session.commit()
        
        # 初始未点赞
        assert init_data['user'].has_liked('post', post.id) is False
        
        # 创建点赞
        like = Like(
            user_id=init_data['user'].id,
            target_type='post',
            target_id=post.id
        )
        db.session.add(like)
        db.session.commit()
        
        # 已点赞
        assert init_data['user'].has_liked('post', post.id) is True


def test_post_soft_delete(app, init_data):
    """测试帖子软删除"""
    with app.app_context():
        from app import db
        post = Post(
            title='待删除',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        db.session.add(post)
        db.session.commit()
        
        post.soft_delete()
        assert post.is_deleted is True
        
        post.restore()
        assert post.is_deleted is False


def test_notification_creation(app, init_data):
    """测试通知创建"""
    with app.app_context():
        from app import db
        notification = Notification(
            user_id=init_data['user'].id,
            title='测试通知',
            message='这是一条测试通知',
            type='system'
        )
        db.session.add(notification)
        db.session.commit()
        
        assert notification.id is not None
        assert notification.is_read is False
