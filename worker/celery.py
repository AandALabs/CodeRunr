from celery import Celery
from config import settings

app = Celery(
    "worker",
    include=["worker.tasks"],
    backend=settings.REDIS_URL,
    broker=settings.REDIS_URL,
    broker_connection_retry_on_startup=True,
    broker_transport_options={
        "visibility_timeout": 3600,
        "retry_policy": {"timeout": 5.0},
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    timezone="Asia/Kolkata",
    enable_utc=True,
)


if __name__ == "__main__":
    app.start()
