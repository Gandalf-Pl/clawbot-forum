"""
测试配置和夹具
"""
import pytest
from app import create_app, db
from app.models import User, Category, Tag, Post, Comment


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建 CLI 测试运行器"""
    return app.test_cli_runner()


@pytest.fixture
def init_data(app):
    """初始化测试数据"""
    with app.app_context():
        # 创建分类
        category = Category(name='技术讨论', description='技术交流', color='#0d6efd')
        db.session.add(category)
        
        # 创建标签
        tag = Tag(name='Python', color='#3776ab')
        db.session.add(tag)
        
        # 创建用户
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        
        db.session.commit()
        
        return {'category': category, 'tag': tag, 'user': user}


class AuthActions:
    """认证操作辅助类"""
    
    def __init__(self, client):
        self._client = client
    
    def login(self, username='testuser', password='testpass'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    """认证夹具"""
    return AuthActions(client)
