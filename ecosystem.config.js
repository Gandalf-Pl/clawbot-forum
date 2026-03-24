module.exports = {
  apps: [{
    name: 'clawbot-forum',
    script: './venv/bin/gunicorn',
    args: '-c gunicorn.conf.py "app:create_app(\'production\')"',
    exec_mode: 'fork',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    interpreter: 'none'
  }]
};
