# OpenClaw 用户论坛

一个基于 Python + Flask + MySQL 的论坛系统，让 OpenClaw 用户可以交流使用经验。

## 功能特性

- **用户系统**：注册、登录、个人资料管理
- **帖子系统**：发帖、编辑、删除、置顶、分类
- **评论系统**：评论、回复、点赞
- **分类标签**：帖子分类和标签管理
- **搜索功能**：全文搜索帖子
- **管理后台**：用户管理、内容审核、系统设置

## 技术栈

- **后端**：Python 3.8+, Flask, Flask-SQLAlchemy, Flask-Login
- **数据库**：MySQL 5.7+
- **前端**：Bootstrap 5, Bootstrap Icons, Vanilla JS
- **其他**：Flask-Migrate（数据库迁移）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/openclaw-forum.git
cd openclaw-forum
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

创建 MySQL 数据库：

```sql
CREATE DATABASE openclaw_forum CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

修改 `config.py` 中的数据库连接信息：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://用户名:密码@localhost/openclaw_forum'
```

### 5. 初始化数据库

```bash
python init_db.py
```

### 6. 运行应用

```bash
python run.py
```

访问 http://localhost:5000

## 默认账号

- **管理员**：admin@example.com / admin123
- **普通用户**：user@example.com / user123

## 项目结构

```
openclaw-forum/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用工厂
│   ├── models.py          # 数据库模型
│   ├── routes/            # 路由蓝图
│   │   ├── auth.py        # 认证相关
│   │   ├── forum.py       # 论坛主逻辑
│   │   ├── admin.py       # 管理后台
│   │   └── api.py         # API接口
│   ├── templates/         # HTML模板
│   └── static/            # 静态文件
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── run.py                 # 启动文件
├── init_db.py             # 数据库初始化
└── README.md              # 说明文档
```

## 部署到生产环境

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name forum.openclaw.ai;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/openclaw-forum/app/static;
    }
}
```

## 配置说明

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `SECRET_KEY` | Flask 密钥 | dev-secret-key |
| `DATABASE_URL` | 数据库连接字符串 | mysql+pymysql://root@localhost/openclaw_forum |
| `MAIL_SERVER` | SMTP 服务器 | None |
| `MAIL_PORT` | SMTP 端口 | 587 |
| `MAIL_USERNAME` | 邮箱账号 | None |
| `MAIL_PASSWORD` | 邮箱密码 | None |

## 开发计划

- [ ] 富文本编辑器（Markdown）
- [ ] 文件上传功能
- [ ] 私信系统
- [ ] 积分/等级系统
- [ ] 邮件通知
- [ ] 第三方登录（GitHub、Google）
- [ ] RESTful API
- [ ] 移动端适配优化

## 贡献指南

1. Fork 项目
2. 创建分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

MIT License

## 联系我们

- GitHub Issues: https://github.com/openclaw/openclaw-forum/issues
- 官方论坛: https://forum.openclaw.ai
