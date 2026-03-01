"""
OpenClaw 论坛系统 - 工具函数
"""
import re
import bleach
import markdown
from datetime import datetime
from flask import Markup


def register_filters(app):
    """注册模板过滤器"""
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """格式化日期时间"""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('timeago')
    def timeago(value):
        """显示相对时间（如：2小时前）"""
        if value is None:
            return ''
        
        now = datetime.utcnow()
        diff = now - value
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return '刚刚'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f'{minutes}分钟前'
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f'{hours}小时前'
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f'{days}天前'
        else:
            return value.strftime('%Y-%m-%d')
    
    @app.template_filter('markdown')
    def render_markdown(text):
        """渲染 Markdown 为 HTML"""
        if not text:
            return ''
        
        # 配置允许的 HTML 标签和属性
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'a', 'img', 'code', 'pre', 'blockquote',
            'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr'
        ]
        allowed_attributes = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title'],
            'code': ['class'],
            'pre': ['class']
        }
        
        # 转换 Markdown
        html = markdown.markdown(
            text,
            extensions=['extra', 'codehilite', 'nl2br'],
            safe_mode='escape'
        )
        
        # 清理 HTML
        clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
        
        return Markup(clean_html)
    
    @app.template_filter('truncate_words')
    def truncate_words(text, length=50):
        """按词数截断文本"""
        if not text:
            return ''
        
        words = text.split()
        if len(words) <= length:
            return text
        return ' '.join(words[:length]) + '...'
    
    @app.template_filter('strip_html')
    def strip_html(text):
        """去除 HTML 标签"""
        if not text:
            return ''
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)


def slugify(text):
    """
    将文本转换为 URL 友好的 slug
    
    例如："Hello World" -> "hello-world"
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def allowed_file(filename, allowed_extensions=None):
    """
    检查文件扩展名是否允许
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名集合，默认从配置读取
    
    Returns:
        bool: 是否允许
    """
    from flask import current_app
    
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_filename(original_filename):
    """
    生成安全的文件名
    
    使用时间戳和随机字符串避免冲突
    """
    import uuid
    from werkzeug.utils import secure_filename
    
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    filename = secure_filename(original_filename.rsplit('.', 1)[0])
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return f"{filename}_{timestamp}_{unique_id}.{ext}" if ext else f"{filename}_{timestamp}_{unique_id}"


def get_client_ip():
    """获取客户端真实 IP"""
    from flask import request
    
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def paginate(query, page, per_page, error_out=False):
    """
    分页辅助函数
    
    Args:
        query: SQLAlchemy 查询对象
        page: 当前页码
        per_page: 每页数量
        error_out: 页码错误时是否抛出异常
    
    Returns:
        Pagination 对象
    """
    return query.paginate(page=page, per_page=per_page, error_out=error_out)
