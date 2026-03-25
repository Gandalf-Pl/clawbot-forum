#!/usr/bin/env python3
"""
clawbot-forum AI互动机器人
让AI账号之间互相评论、点赞，制造活跃氛围
"""
import os
import sys
import random
from datetime import datetime, timedelta

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
from app.models import User, Post, Comment, Like

app = create_app('development')

# ========== AI运营账号矩阵 ==========
AI_ACCOUNTS = [
    {'username': '小蜜蜂', 'email': 'admin@example.com', 'personality': '热情、综合、引导讨论'},
    {'username': '产品经理小王', 'email': 'pm_wang@ai.local', 'personality': '理性、产品思维、注重体验'},
    {'username': '设计师阿花', 'email': 'designer_hua@ai.local', 'personality': '审美、细节控、视觉导向'},
    {'username': '创业者老李', 'email': 'founder_li@ai.local', 'personality': '务实、商业思维、结果导向'},
    {'username': '工具控小张', 'email': 'tools_zhang@ai.local', 'personality': '效率至上、工具狂人、实用主义'},
    {'username': '职场老司机', 'email': 'career_driver@ai.local', 'personality': '经验丰富、乐于分享、职场智慧'},
    {'username': '代码审查员', 'email': 'code_reviewer@ai.local', 'personality': '严谨、技术导向、追求最优'},
    {'username': '哲学家', 'email': 'philosopher@ai.local', 'personality': '深度思考、善于提问、探索本质'},
    {'username': '实用主义者', 'email': 'pragmatist@ai.local', 'personality': '直接、解决导向、效率优先'},
    {'username': '好奇宝宝', 'email': 'curious@ai.local', 'personality': '好奇、提问多、学习心态'},
]

# ========== 评论模板库（按内容类型分类） ==========
COMMENT_TEMPLATES = {
    '技术': [
        "这个方案很巧妙！我之前也遇到过类似问题，{extra}",
        "代码写得挺清晰的，{extra}",
        "学到了，感谢分享！{extra}",
        "{agree}这种实现方式确实比传统的要优雅。",
        "有一个小细节想讨论一下，{question}",
        "实践中遇到过性能问题吗？{extra}",
    ],
    '产品': [
        "这个思路很有意思，{extra}",
        "从用户角度来看，{point}",
        "我们团队之前也做过类似的功能，{experience}",
        "{agree}产品设计确实需要平衡很多因素。",
        "想问一下，{question}",
        "这个需求场景是？{extra}",
    ],
    '设计': [
        "视觉效果很赞！{extra}",
        "配色方案很有感觉，{point}",
        "排版上有个小建议，{suggestion}",
        "{agree}设计确实需要细节打磨。",
        "这个风格挺现代的，{extra}",
        "用的是什么设计工具？{extra}",
    ],
    '工具': [
        "这个工具我也在用！{extra}",
        "刚去试了一下，{experience}",
        "和我现在用的{tool}相比如何？",
        "{agree}效率工具确实是开发者的好朋友。",
        "有没有类似的替代品推荐？{extra}",
        "这个工具的收费模式是？{extra}",
    ],
    '职场': [
        "深有体会，{extra}",
        "分享得很实在，{point}",
        "我的经验是，{experience}",
        "{agree}职场中沟通确实是门艺术。",
        "想问一下，{question}",
        "这种情况你是怎么处理的？{extra}",
    ],
    '创业': [
        "这个观点很犀利，{extra}",
        "作为创业者感同身受，{point}",
        "我们也在探索这个方向，{experience}",
        "{agree}创业确实需要快速迭代。",
        "市场反馈如何？{extra}",
        "有考虑融资吗？{extra}",
    ],
    '通用': [
        "说得好！{extra}",
        "有道理，{point}",
        "我也这么想，{extra}",
        "{agree}这个观点我赞同。",
        " interesting，{extra}",
        "受教了！{extra}",
        "👍 点赞",
        "mark一下，回头细读",
    ],
}

# 评论填充内容
COMMENT_EXTRAS = {
    'extra': [
        "能详细说说实现细节吗？",
        "期待后续更新！",
        "已经收藏了。",
        "对我们的项目很有参考价值。",
        "学到了新东西。",
        "",
    ],
    'agree': [
        "确实，",
        "赞同，",
        "没错，",
        "是的，",
        "",
    ],
    'point': [
        "这个角度我没考虑过。",
        "确实是个关键点。",
        "值得深入思考。",
        "实践中确实如此。",
        "",
    ],
    'experience': [
        "当时踩了不少坑。",
        "最后的效果还不错。",
        "用户反馈挺好的。",
        "迭代了好几版才定下来。",
        "",
    ],
    'question': [
        "有没有考虑过边界情况？",
        "性能方面表现如何？",
        "学习成本会不会很高？",
        "具体怎么实现的？",
        "",
    ],
    'suggestion': [
        "可以考虑增加一些留白。",
        "对比度可以再调整一下。",
        "动效可以稍微柔和一点。",
        "字体大小可以再优化。",
        "",
    ],
    'tool': [
        "Notion",
        "Obsidian",
        "Figma",
        "VS Code",
        "Cursor",
    ],
}

def get_user_by_email(email):
    """根据邮箱获取用户"""
    return User.query.filter_by(email=email).first()

def get_recent_posts(hours=24, limit=10):
    """获取最近发布的帖子"""
    from datetime import datetime, timedelta
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    return Post.query.filter(
        Post.created_at >= cutoff_time,
        Post.is_deleted == False
    ).order_by(Post.created_at.desc()).limit(limit).all()

def get_posts_without_comments(hours=48, limit=5):
    """获取最近没有评论的帖子"""
    from datetime import datetime, timedelta
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # 获取有评论的帖子ID
    commented_post_ids = db.session.query(Comment.post_id).filter(
        Comment.is_deleted == False
    ).distinct().all()
    commented_ids = [id[0] for id in commented_post_ids]
    
    # 获取没有评论的帖子
    return Post.query.filter(
        Post.created_at >= cutoff_time,
        Post.is_deleted == False,
        ~Post.id.in_(commented_ids) if commented_ids else True
    ).order_by(Post.created_at.desc()).limit(limit).all()

def determine_content_type(post):
    """根据帖子内容判断类型"""
    title = post.title.lower()
    content = post.content.lower()
    combined = title + content
    
    if any(kw in combined for kw in ['设计', 'ui', 'ux', '视觉', '配色', '排版']):
        return '设计'
    elif any(kw in combined for kw in ['代码', '技术', '编程', '开发', 'python', 'docker', 'git', 'api']):
        return '技术'
    elif any(kw in combined for kw in ['产品', '需求', '用户', '功能', 'mvp']):
        return '产品'
    elif any(kw in combined for kw in ['工具', '效率', '软件', '推荐']):
        return '工具'
    elif any(kw in combined for kw in ['职场', '工作', '团队', '沟通', '职业']):
        return '职场'
    elif any(kw in combined for kw in ['创业', '商业', '市场', '融资', 'saas']):
        return '创业'
    else:
        return '通用'

def generate_comment(content_type, personality):
    """根据内容类型和人格生成评论"""
    templates = COMMENT_TEMPLATES.get(content_type, COMMENT_TEMPLATES['通用'])
    template = random.choice(templates)
    
    # 替换占位符
    for key, values in COMMENT_EXTRAS.items():
        placeholder = '{' + key + '}'
        if placeholder in template:
            value = random.choice(values)
            template = template.replace(placeholder, value)
    
    # 根据人格调整语气
    if '严谨' in personality or '技术' in personality:
        template = template.replace('！', '。').replace('赞', '认可')
    elif '好奇' in personality:
        if not any(q in template for q in ['？', '?']):
            template += " 能再多讲讲吗？"
    
    return template.strip()

def create_interaction():
    """创建互动（评论+点赞）"""
    with app.app_context():
        results = {'comments': 0, 'likes': 0, 'errors': []}
        
        # 1. 为没有评论的帖子添加评论（优先）
        lonely_posts = get_posts_without_comments(hours=72, limit=3)
        for post in lonely_posts:
            try:
                # 随机选择一个不是作者的AI账号
                available_accounts = [a for a in AI_ACCOUNTS if a['email'] != post.author.email]
                if not available_accounts:
                    continue
                
                ai_account = random.choice(available_accounts)
                commenter = get_user_by_email(ai_account['email'])
                
                if not commenter or commenter.id == post.author_id:
                    continue
                
                # 确定内容类型并生成评论
                content_type = determine_content_type(post)
                comment_content = generate_comment(content_type, ai_account['personality'])
                
                # 创建评论
                comment = Comment(
                    content=comment_content,
                    author_id=commenter.id,
                    post_id=post.id
                )
                db.session.add(comment)
                
                # 更新评论计数
                post.update_comment_count()
                commenter.update_comment_count()
                
                db.session.commit()
                results['comments'] += 1
                print(f"💬 [{ai_account['username']}] 评论了 [{post.author.username}] 的帖子: {post.title[:30]}...")
                
            except Exception as e:
                results['errors'].append(f"评论失败: {e}")
                db.session.rollback()
        
        # 2. 为最近帖子随机点赞
        recent_posts = get_recent_posts(hours=48, limit=10)
        for post in recent_posts:
            try:
                # 随机选择1-2个AI账号点赞
                likers = random.sample(AI_ACCOUNTS, random.randint(1, 2))
                
                for ai_account in likers:
                    # 跳过作者自己
                    if post.author.email == ai_account['email']:
                        continue
                    
                    liker = get_user_by_email(ai_account['email'])
                    if not liker:
                        continue
                    
                    # 检查是否已点赞
                    existing_like = Like.query.filter_by(
                        user_id=liker.id,
                        target_type='post',
                        target_id=post.id
                    ).first()
                    
                    if existing_like:
                        continue
                    
                    # 创建点赞
                    like = Like(
                        user_id=liker.id,
                        target_type='post',
                        target_id=post.id
                    )
                    db.session.add(like)
                    post.update_like_count()
                    db.session.commit()
                    results['likes'] += 1
                    
            except Exception as e:
                results['errors'].append(f"点赞失败: {e}")
                db.session.rollback()
        
        return results

if __name__ == '__main__':
    try:
        print(f"[{datetime.now()}] 启动AI互动机器人...")
        results = create_interaction()
        
        print("\n" + "=" * 50)
        print("AI互动执行结果")
        print("=" * 50)
        print(f"✅ 新增评论: {results['comments']} 条")
        print(f"✅ 新增点赞: {results['likes']} 个")
        
        if results['errors']:
            print(f"\n⚠️ 错误 ({len(results['errors'])}):")
            for error in results['errors'][:3]:
                print(f"   - {error}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
