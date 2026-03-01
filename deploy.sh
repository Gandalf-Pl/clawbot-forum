#!/bin/bash
# OpenClaw 论坛部署脚本

set -e

echo "=== OpenClaw 论坛部署脚本 ==="

# 检查参数
ENV=${1:-production}

echo "部署环境: $ENV"

# 安装依赖
echo "[1/5] 安装依赖..."
pip install -r requirements.txt

# 初始化数据库
echo "[2/5] 初始化数据库..."
python init_db.py

# 运行测试
echo "[3/5] 运行单元测试..."
python -m pytest tests/ -v --tb=short

if [ $? -ne 0 ]; then
    echo "测试失败，停止部署"
    exit 1
fi

# 收集静态文件
echo "[4/5] 收集静态文件..."
mkdir -p app/static/uploads

# 启动应用
echo "[5/5] 启动应用..."
if [ "$ENV" = "docker" ]; then
    echo "使用 Docker 部署..."
    docker-compose up -d --build
    echo "应用已启动，访问 http://localhost"
else
    echo "使用 Gunicorn 启动..."
    gunicorn -c gunicorn.conf.py "app:create_app('$ENV')"
fi

echo "=== 部署完成 ==="
