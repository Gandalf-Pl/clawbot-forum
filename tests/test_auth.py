"""
认证模块单元测试
"""
import pytest
from app.models import User


def test_register_page(client):
    """测试注册页面"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'注册' in response.data


def test_register_success(client, app):
    """测试成功注册"""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'new@example.com'


def test_register_duplicate_username(client, init_data):
    """测试重复用户名注册"""
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'another@example.com',
        'password': 'password123',
        'password2': 'password123'
    })
    
    assert b'用户名已被使用' in response.data


def test_register_password_mismatch(client):
    """测试密码不匹配"""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'password2': 'different'
    })
    
    assert b'两次输入的密码不一致' in response.data


def test_login_page(client):
    """测试登录页面"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'登录' in response.data


def test_login_success(client, auth, init_data):
    """测试成功登录"""
    response = auth.login()
    assert response.status_code == 302  # 重定向


def test_login_invalid_password(client, init_data):
    """测试错误密码"""
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'wrongpass'
    })
    assert b'用户名或密码错误' in response.data


def test_logout(client, auth, init_data):
    """测试登出"""
    auth.login()
    response = auth.logout()
    assert response.status_code == 302


def test_profile_page(client, auth, init_data):
    """测试个人资料页面"""
    auth.login()
    response = client.get('/auth/profile')
    assert response.status_code == 200
    assert b'testuser' in response.data


def test_edit_profile(client, auth, init_data):
    """测试编辑个人资料"""
    auth.login()
    response = client.post('/auth/profile/edit', data={
        'bio': '这是我的简介',
        'website': 'https://example.com',
        'location': '北京'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'资料已更新' in response.data


def test_change_password(client, auth, init_data):
    """测试修改密码"""
    auth.login()
    response = client.post('/auth/change-password', data={
        'current_password': 'testpass',
        'new_password': 'newpass123',
        'new_password2': 'newpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'密码已修改' in response.data


def test_user_profile_page(client, init_data):
    """测试用户公开资料页"""
    response = client.get('/user/testuser')
    assert response.status_code == 200
    assert b'testuser' in response.data
