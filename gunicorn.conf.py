import multiprocessing

# 绑定地址
bind = "127.0.0.1:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 每个工作进程的线程数
threads = 4

# 最大并发连接数
worker_connections = 1000

# 超时时间（秒）
timeout = 120
keepalive = 5

# 日志配置
accesslog = "-"  # 输出到 stdout
errorlog = "-"   # 输出到 stderr
loglevel = "info"

# 进程名称
proc_name = "openclaw-forum"

# 守护进程（Docker 中设为 False）
daemon = False

# 预加载应用
preload_app = True

# 重启前处理
max_requests = 1000
max_requests_jitter = 50
