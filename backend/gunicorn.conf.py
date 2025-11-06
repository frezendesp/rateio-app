import multiprocessing
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
log_dir = project_root.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
accesslog = log_dir / "gunicorn.log"
errorlog = log_dir / "gunicorn.log"
loglevel = "info"
