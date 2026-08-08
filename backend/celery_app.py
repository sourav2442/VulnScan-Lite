from celery import Celery

celery = Celery(
    "vulnscan",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks.scan_tasks"],   # <-- Tell Celery where the tasks are
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)