#!/usr/bin/env python3
"""
OpenClaw 论坛系统 - 启动文件
"""
import os
from app import create_app

# 获取环境配置
config_name = os.environ.get('FLASK_ENV') or 'development'
app = create_app(config_name)

if __name__ == '__main__':
    # 开发服务器配置
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', True)
    )
