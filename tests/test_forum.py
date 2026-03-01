"""
论坛功能单元测试
"""
import pytest
from app.models import Post, Comment, Like


def test_index_page(client, init_data):
    """测试首页"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'OpenClaw 论坛' in response.data


def test_category_page(client, init_data):
    """测试分类页面"""
    response = client.get(f'/category/{init_data["category"].id}')
    assert response.status_code == 200
    assert b'技术讨论' in response.data


def test_create_post_page_requires_login(client):
    """测试发帖需要登录"""
    response = client.get('/post/create', follow_redirects=True)
    assert b'请先登录' in response.data


def test_create_post(client, auth, init_data):
    """测试创建帖子"""
    auth.login()
    response = client.post('/post/create', data={
        'title': '测试帖子标题',
        'content': '这是测试内容',
        'category_id': init_data['category'].id,
        'tags': 'Python,Flask'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'帖子已发布' in response.data


def test_post_detail_page(client, init_data, app):
    """测试帖子详情页"""
    with app.app_context():
        post = Post(
            title='测试帖子',
            content='测试内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        from app import db
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    response = client.get(f'/post/{post_id}')
    assert response.status_code == 200
    assert b'测试帖子' in response.data


def test_edit_post(client, auth, init_data, app):
    """测试编辑帖子"""
    with app.app_context():
        post = Post(
            title='原标题',
            content='原内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        from app import db
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    auth.login()
    response = client.post(f'/post/{post_id}/edit', data={
        'title': '修改后的标题',
        'content': '修改后的内容',
        'category_id': init_data['category'].id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'修改后的标题' in response.data


def test_delete_post(client, auth, init_data, app):
    """测试删除帖子"""
    with app.app_context():
        post = Post(
            title='待删除',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        from app import db
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    auth.login()
    response = client.post(f'/post/{post_id}/delete', follow_redirects=True)
    assert response.status_code == 200


def test_add_comment(client, auth, init_data, app):
    """测试添加评论"""
    with app.app_context():
        post = Post(
            title='测试帖子',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        from app import db
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    auth.login()
    response = client.post(f'/post/{post_id}/comment', data={
        'content': '这是一条评论'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'评论已发布' in response.data


def test_like_post(client, auth, init_data, app):
    """测试点赞帖子"""
    with app.app_context():
        post = Post(
            title='测试帖子',
            content='内容',
            author_id=init_data['user'].id,
            category_id=init_data['category'].id
        )
        from app import db
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    auth.login()
    response = client.post(f'/api/like', json={
        'type': 'post',
        'id': post_id
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_search_page(client):
    """测试搜索页面"""
    response = client.get('/search?q=测试')
    assert response.status_code == 200


def test_tags_page(client, init_data):
    """测试标签页面"""
    response = client.get('/tags')
    assert response.status_code == 200


def test_users_page(client):
    """测试用户列表页面"""
    response = client.get('/users')
    assert response.status_code == 200
