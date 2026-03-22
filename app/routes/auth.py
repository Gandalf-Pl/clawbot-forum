"""
OpenClaw 论坛系统 - 认证路由
处理用户注册、登录、登出等功能
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.models import User
from app.utils import allowed_file, generate_filename
from app.utils_avatar import ensure_user_avatar, generate_default_avatar
import os

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('forum.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # 验证输入
        errors = []
        
        if not username or len(username) < 3 or len(username) > 20:
            errors.append('用户名长度必须在 3-20 个字符之间')
        
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            errors.append('用户名只能包含字母、数字、下划线和中文')
        
        if User.query.filter_by(username=username).first():
            errors.append('用户名已被使用')
        
        if not email or '@' not in email:
            errors.append('请输入有效的邮箱地址')
        
        if User.query.filter_by(email=email).first():
            errors.append('邮箱已被注册')
        
        if len(password) < 6:
            errors.append('密码长度至少为 6 个字符')
        
        if password != password_confirm:
            errors.append('两次输入的密码不一致')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', 
                                 username=username, email=email)
        
        # 创建用户
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 生成用户头像
        try:
            from flask import current_app
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            avatar_filename = ensure_user_avatar(username, upload_folder)
            user.avatar = avatar_filename
            db.session.commit()
        except Exception as e:
            # 头像生成失败不影响注册
            print(f"头像生成失败: {e}")
        
        flash('注册成功！请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('forum.index'))
    
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        # 支持用户名或邮箱登录
        user = User.query.filter(
            db.or_(
                User.username == username_or_email,
                User.email == username_or_email.lower()
            )
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('您的账号已被禁用，请联系管理员', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            user.update_last_seen()
            
            flash(f'欢迎回来，{user.username}！', 'success')
            
            # 跳转到之前访问的页面
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('forum.index')
            
            return redirect(next_page)
        else:
            flash('用户名/邮箱或密码错误', 'danger')
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('forum.index'))


@bp.route('/profile')
@login_required
def profile():
    """个人资料页"""
    return render_template('auth/profile.html', user=current_user)


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料"""
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        website = request.form.get('website', '').strip()
        location = request.form.get('location', '').strip()
        
        # 验证
        if len(bio) > 500:
            flash('个人简介不能超过 500 个字符', 'danger')
            return render_template('auth/edit_profile.html')
        
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        
        # 处理头像上传
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename and allowed_file(file.filename):
                filename = generate_filename(file.filename)
                upload_folder = current_user._get_current_object().app.config['UPLOAD_FOLDER']
                
                # 确保上传目录存在
                os.makedirs(upload_folder, exist_ok=True)
                
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                
                # 删除旧头像（如果不是默认头像）
                if current_user.avatar and current_user.avatar != 'default-avatar.png':
                    old_path = os.path.join(upload_folder, current_user.avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                current_user.avatar = filename
        
        current_user.bio = bio
        current_user.website = website
        current_user.location = location
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html')


@bp.route('/password/change', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # 验证
        if not current_user.check_password(current_password):
            flash('当前密码不正确', 'danger')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('新密码长度至少为 6 个字符', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'danger')
            return render_template('auth/change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('密码修改成功', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')


@bp.route('/user/<username>')
def user_profile(username):
    """查看其他用户资料"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # 获取用户的帖子
    page = request.args.get('page', 1, type=int)
    posts = user.posts.filter_by(is_deleted=False).order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('auth/user_profile.html', user=user, posts=posts)


# 导入需要的模块
import re
from flask import current_app
from app.models import Post
