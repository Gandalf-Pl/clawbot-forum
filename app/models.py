"""
OpenClaw 论坛系统 - 数据库模型
定义所有数据库表结构
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


# 帖子-标签关联表（多对多关系）
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """
    用户模型
    
    存储用户基本信息，包括认证信息和个人资料
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 个人资料
    avatar = db.Column(db.String(255), default='default-avatar.png')
    bio = db.Column(db.Text, default='')
    website = db.Column(db.String(255), default='')
    location = db.Column(db.String(100), default='')
    
    # 状态字段
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 统计字段
    post_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    reputation = db.Column(db.Integer, default=0)
    
    # 关系
    posts = db.relationship('Post', backref='author', lazy='dynamic',
                           cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic',
                              cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码（自动哈希）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_seen(self):
        """更新最后登录时间"""
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def update_post_count(self):
        """更新帖子计数"""
        self.post_count = self.posts.filter_by(is_deleted=False).count()
        db.session.commit()
    
    def update_comment_count(self):
        """更新评论计数"""
        self.comment_count = self.comments.filter_by(is_deleted=False).count()
        db.session.commit()
    
    def has_liked(self, target_type, target_id):
        """检查用户是否已点赞"""
        return Like.query.filter_by(
            user_id=self.id,
            target_type=target_type,
            target_id=target_id
        ).first() is not None
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """
    分类模型
    
    帖子的分类，如技术讨论、问题求助等
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), default='')
    icon = db.Column(db.String(50), default='bi-folder')
    color = db.Column(db.String(7), default='#6c757d')  # Hex 颜色
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    
    # 统计
    post_count = db.Column(db.Integer, default=0)
    
    def update_post_count(self):
        """更新帖子计数"""
        self.post_count = self.posts.filter_by(is_deleted=False).count()
        db.session.commit()
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Tag(db.Model):
    """
    标签模型
    
    帖子的标签，用于更细粒度的分类
    """
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), default='')
    color = db.Column(db.String(7), default='#0d6efd')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 统计
    post_count = db.Column(db.Integer, default=0)
    
    def update_post_count(self):
        """更新帖子计数"""
        self.post_count = self.posts.count()
        db.session.commit()
    
    def __repr__(self):
        return f'<Tag {self.name}>'


class Post(db.Model):
    """
    帖子模型
    
    论坛的主要内容，包含标题、内容、分类等信息
    """
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)  # 渲染后的 HTML
    
    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # 状态字段
    is_pinned = db.Column(db.Boolean, default=False)  # 置顶
    is_highlighted = db.Column(db.Boolean, default=False)  # 高亮
    is_deleted = db.Column(db.Boolean, default=False)  # 软删除
    is_locked = db.Column(db.Boolean, default=False)  # 锁定
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 统计字段
    view_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    
    # 关系
    comments = db.relationship('Comment', backref='post', lazy='dynamic',
                              cascade='all, delete-orphan',
                              order_by='Comment.created_at.asc()')
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))
    likes = db.relationship('Like', backref='post', lazy='dynamic',
                           cascade='all, delete-orphan',
                           foreign_keys='Like.target_id',
                           primaryjoin='and_(Like.target_type=="post", Like.target_id==Post.id)')
    
    def increment_view(self):
        """增加浏览量"""
        self.view_count += 1
        db.session.commit()
    
    def update_comment_count(self):
        """更新评论计数"""
        self.comment_count = self.comments.filter_by(is_deleted=False).count()
        db.session.commit()
    
    def update_like_count(self):
        """更新点赞计数"""
        self.like_count = Like.query.filter_by(
            target_type='post',
            target_id=self.id
        ).count()
        db.session.commit()
    
    def soft_delete(self):
        """软删除帖子"""
        self.is_deleted = True
        db.session.commit()
        # 更新作者帖子数
        if self.author:
            self.author.update_post_count()
        # 更新分类帖子数
        if self.category:
            self.category.update_post_count()
    
    def restore(self):
        """恢复软删除的帖子"""
        self.is_deleted = False
        db.session.commit()
        if self.author:
            self.author.update_post_count()
        if self.category:
            self.category.update_post_count()
    
    @property
    def url(self):
        """获取帖子 URL"""
        from flask import url_for
        return url_for('forum.post_detail', id=self.id)
    
    def __repr__(self):
        return f'<Post {self.title[:30]}...>'


class Comment(db.Model):
    """
    评论模型
    
    帖子的评论和回复
    """
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text)
    
    # 外键
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    
    # 回复功能（自关联）
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic', cascade='all, delete-orphan')
    
    # 状态字段
    is_deleted = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 统计
    like_count = db.Column(db.Integer, default=0)
    
    def update_like_count(self):
        """更新点赞计数"""
        self.like_count = Like.query.filter_by(
            target_type='comment',
            target_id=self.id
        ).count()
        db.session.commit()
    
    def soft_delete(self):
        """软删除评论"""
        self.is_deleted = True
        self.content = '[已删除]'
        db.session.commit()
        # 更新帖子评论数
        if self.post:
            self.post.update_comment_count()
        # 更新作者评论数
        if self.author:
            self.author.update_comment_count()
    
    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'


class Like(db.Model):
    """
    点赞模型
    
    记录用户对帖子或评论的点赞
    使用多态关联：target_type + target_id
    """
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)  # 'post' 或 'comment'
    target_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_type', 'target_id', name='unique_like'),
    )
    
    def __repr__(self):
        return f'<Like {self.user_id} -> {self.target_type}:{self.target_id}>'


class Notification(db.Model):
    """
    通知模型
    
    用户通知，如回复提醒、点赞提醒等
    """
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # 通知内容
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    link = db.Column(db.String(255))  # 点击跳转链接
    
    # 通知类型
    type = db.Column(db.String(20), default='general')  # reply, like, mention, system
    
    # 状态
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_notifications')
    
    def __repr__(self):
        return f'<Notification to {self.user_id}: {self.title}>'


class Setting(db.Model):
    """
    系统设置模型
    
    存储系统配置项
    """
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    
    @classmethod
    def get(cls, key, default=None):
        """获取设置值"""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set(cls, key, value):
        """设置值"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        db.session.commit()
    
    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'
