from .settings import settings

wsgi_app = f"{settings.app_name}.main:app"

# logging
log_level = settings.loguru_level
# default: gunicorn.glogger.Logger  # noqa: ERA001
logger_class = f"{settings.app_name}.gunicorn.GunicornLogger"

# server mechanics
# worker_tmp_dir = "/dev/shm"  # default: None  # noqa: ERA001, RUF100, S108

# server socket
bind = [f"{settings.host}:{settings.port}"]  # default: ["127.0.0.1:8000"]

# worker processes
workers = settings.web_concurrency  # default: 1
worker_class = f"{settings.app_name}.gunicorn.UvicornWorker"  # default: "sync"
max_requests = 1000  # default: 0
max_requests_jitter = 100  # default: 0
