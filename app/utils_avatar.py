"""
头像生成工具
为每个用户生成基于用户名的唯一头像
"""
import hashlib
from PIL import Image, ImageDraw
import os


def generate_avatar(username, size=200, output_path=None):
    """
    基于用户名生成 identicon 风格头像
    
    Args:
        username: 用户名
        size: 头像尺寸（像素）
        output_path: 输出路径
    
    Returns:
        生成的文件名
    """
    # 从用户名生成确定性哈希
    hash_obj = hashlib.md5(username.encode('utf-8')).hexdigest()
    
    # 使用哈希值生成颜色
    color_r = int(hash_obj[0:2], 16)
    color_g = int(hash_obj[2:4], 16)
    color_b = int(hash_obj[4:6], 16)
    bg_color = (color_r, color_g, color_b)
    
    # 生成辅助色（较亮）
    fg_color = (
        min(255, color_r + 60),
        min(255, color_g + 60),
        min(255, color_b + 60)
    )
    
    # 创建图像
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 网格大小（5x5）
    grid_size = 5
    cell_size = size // grid_size
    
    # 从哈希生成图案（对称）
    pattern = []
    for i in range(grid_size * 3):  # 只需要左半边
        pattern.append(int(hash_obj[i % 32], 16) % 2 == 0)
    
    # 绘制图案（左右对称）
    for row in range(grid_size):
        for col in range((grid_size + 1) // 2):  # 只绘制左半边
            idx = row * 3 + col
            if idx < len(pattern) and pattern[idx]:
                # 左半边
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                draw.rectangle([x1, y1, x2, y2], fill=fg_color)
                
                # 右半边（对称）
                mirror_col = grid_size - 1 - col
                x1 = mirror_col * cell_size
                x2 = x1 + cell_size
                draw.rectangle([x1, y1, x2, y2], fill=fg_color)
    
    # 保存
    if output_path is None:
        output_path = f"avatar_{username}.png"
    
    img.save(output_path)
    return os.path.basename(output_path)


def get_avatar_filename(username):
    """获取用户的头像文件名"""
    return f"avatar_{hashlib.md5(username.encode('utf-8')).hexdigest()[:8]}.png"


def ensure_user_avatar(username, upload_folder):
    """
    确保用户有头像，如果没有则生成
    
    Args:
        username: 用户名
        upload_folder: 上传文件夹路径
    
    Returns:
        头像文件名
    """
    filename = get_avatar_filename(username)
    filepath = os.path.join(upload_folder, filename)
    
    if not os.path.exists(filepath):
        generate_avatar(username, size=200, output_path=filepath)
    
    return filename


def generate_default_avatar(upload_folder):
    """生成默认头像"""
    filepath = os.path.join(upload_folder, 'default-avatar.png')
    
    # 创建深色主题的默认头像
    size = 200
    img = Image.new('RGB', (size, size), (26, 26, 37))  # 深色背景
    draw = ImageDraw.Draw(img)
    
    # 绘制一个圆形背景
    center = size // 2
    radius = size // 3
    
    # 外圈
    draw.ellipse(
        [center - radius - 5, center - radius - 5, 
         center + radius + 5, center + radius + 5],
        fill=(0, 212, 255),  # 主色调青色
        outline=(0, 212, 255),
        width=2
    )
    
    # 内圈
    draw.ellipse(
        [center - radius, center - radius, 
         center + radius, center + radius],
        fill=(26, 26, 37)  # 深色填充
    )
    
    # 绘制用户图标（简单的头部和肩膀）
    head_radius = radius // 3
    draw.ellipse(
        [center - head_radius, center - radius//2 - head_radius,
         center + head_radius, center - radius//2 + head_radius],
        fill=(0, 212, 255)  # 青色头部
    )
    
    # 身体
    body_points = [
        (center, center + radius//3),
        (center - radius//2, center + radius - 5),
        (center + radius//2, center + radius - 5)
    ]
    draw.polygon(body_points, fill=(0, 212, 255))  # 青色身体
    
    img.save(filepath)
    return 'default-avatar.png'
