# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 2
timeout = 120
keepalive = 2
max_requests = 1000
preload_app = True