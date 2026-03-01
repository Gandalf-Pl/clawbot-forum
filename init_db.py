#!/usr/bin/env python3
"""
OpenClaw 论坛系统 - 数据库初始化脚本
"""
import sys
from app import create_app, db
from app.models import User, Category, Tag, Post, Comment, Like


def init_database():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        print("正在创建数据库表...")
        
        # 创建所有表
        db.create_all()
        
        # 检查是否已有分类
        if Category.query.first() is None:
            print("正在创建默认分类...")
            # 创建默认分类
            default_categories = [
                Category(name='综合讨论', description='一般性话题讨论', sort_order=1),
                Category(name='技术交流', description='技术问题讨论与分享', sort_order=2),
                Category(name='问题求助', description='遇到问题？来这里求助', sort_order=3),
                Category(name='资源分享', description='分享有用的资源和工具', sort_order=4),
                Category(name='公告通知', description='官方公告和重要通知', sort_order=0),
            ]
            for cat in default_categories:
                db.session.add(cat)
            
            db.session.commit()
            print(f"已创建 {len(default_categories)} 个默认分类")
        
        # 检查是否已有标签
        if Tag.query.first() is None:
            print("正在创建默认标签...")
            default_tags = [
                Tag(name='Python'),
                Tag(name='Flask'),
                Tag(name='MySQL'),
                Tag(name='前端'),
                Tag(name='后端'),
                Tag(name='教程'),
                Tag(name='问题'),
                Tag(name='分享'),
            ]
            for tag in default_tags:
                db.session.add(tag)
            
            db.session.commit()
            print(f"已创建 {len(default_tags)} 个默认标签")
        
        print("数据库初始化完成！")
        print("\n提示：")
        print("1. 运行 'python run.py' 启动应用")
        print("2. 注册第一个用户后，在数据库中设置 is_admin=1 使其成为管理员")
        print("3. 管理员可以访问 /admin 进入管理后台")


if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"初始化失败: {e}")
        sys.exit(1)
