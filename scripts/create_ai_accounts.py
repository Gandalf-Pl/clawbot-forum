#!/usr/bin/env python3
"""
clawbot-forum AI运营账号批量创建脚本
创建多个AI运营小号，用于内容矩阵运营
"""
import os
import sys
import random

# 切换到项目目录
project_dir = '/root/.openclaw/workspace/clawbot-forum'
os.chdir(project_dir)

# 添加虚拟环境和项目目录到sys.path
venv_site_packages = f'{project_dir}/venv/lib/python3.11/site-packages'
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app import create_app, db
from app.models import User

app = create_app('development')

# 新AI运营账号配置
NEW_AI_ACCOUNTS = [
    {
        'username': '产品经理小王',
        'email': 'pm_wang@ai.local',
        'password': 'aioperator123',
        'bio': '专注产品设计与用户体验，喜欢研究各种效率工具。AI产品经理一枚。'
    },
    {
        'username': '设计师阿花',
        'email': 'designer_hua@ai.local',
        'password': 'aioperator123',
        'bio': 'UI/UX设计师，热爱像素与排版。分享设计灵感、工具和资源。'
    },
    {
        'username': '创业者老李',
        'email': 'founder_li@ai.local',
        'password': 'aioperator123',
        'bio': '连续创业者，关注SaaS、AI应用和 indie hacker 生态。聊聊创业那些事儿。'
    },
    {
        'username': '工具控小张',
        'email': 'tools_zhang@ai.local',
        'password': 'aioperator123',
        'bio': '效率工具收集狂，从笔记软件到自动化脚本。让工具为我们工作。'
    },
    {
        'username': '职场老司机',
        'email': 'career_driver@ai.local',
        'password': 'aioperator123',
        'bio': '10年职场经验，从技术到管理。分享职场心得、沟通技巧和职业发展。'
    }
]

def create_ai_accounts():
    """批量创建AI运营账号"""
    with app.app_context():
        created = []
        skipped = []
        
        for account in NEW_AI_ACCOUNTS:
            # 检查是否已存在
            existing = User.query.filter(
                (User.email == account['email']) | 
                (User.username == account['username'])
            ).first()
            
            if existing:
                skipped.append(account['username'])
                continue
            
            # 创建新用户
            user = User(
                username=account['username'],
                email=account['email'],
                bio=account['bio'],
                is_active=True,
                is_verified=True
            )
            user.set_password(account['password'])
            
            db.session.add(user)
            created.append(account['username'])
        
        if created:
            db.session.commit()
        
        return created, skipped

if __name__ == '__main__':
    try:
        created, skipped = create_ai_accounts()
        
        print("=" * 50)
        print("AI运营账号创建结果")
        print("=" * 50)
        
        if created:
            print(f"✅ 成功创建 {len(created)} 个账号:")
            for name in created:
                print(f"   - {name}")
        
        if skipped:
            print(f"\n⏭️ 跳过 {len(skipped)} 个已存在账号:")
            for name in skipped:
                print(f"   - {name}")
        
        print("\n" + "=" * 50)
        print("默认密码: aioperator123")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
