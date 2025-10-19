import logging
from time import timezone

from celery import Celery, Task
from kombu import Queue, Exchange

from core.config import settings

BROKER_URL = f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}{settings.RABBITMQ_DEFAULT_VHOST}"

celery_app = Celery("tasks")

TASK_DEFAULT_QUEUE = "high"
TASK_DEFAULT_ROUTING_KEY = "high"
TASK_DEFAULT_EXCHANGE = "high"

TASKS_QUEUES = [
    Queue("high", Exchange("high"), routing_key="high"),
    Queue("low", Exchange("low"), routing_key="low"),
    Queue("ollama_manage", Exchange("ollama_manage"), routing_key="ollama_manage"),
]

TASK_ROUTES = {
    # Пример подключения таски
    # 'tasks.email.*': {'queue': 'low'},
}

celery_app.conf.update(
    broker_url=BROKER_URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=timezone,
    enable_utc=True,
    task_default_queue=TASK_DEFAULT_QUEUE,
    task_default_exchange=TASK_DEFAULT_EXCHANGE,
    task_default_routing_key=TASK_DEFAULT_ROUTING_KEY,
    task_queues=TASKS_QUEUES,
    imports=("tasks",),
    task_acks_late=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    task_routes=TASK_ROUTES,
)

class CeleryTaskWithLogging(Task):
    """Base Celery Task with self.logger and automatic lifecycle logging."""

    @property
    def logger(self):
        return logging.getLogger(f"|celery.task.{self.name}|")

    def __call__(self, *args, **kwargs):
        self.logger.info(
            "Задача запущена",
            extra={
                "task_name": self.name,
                "task_id": self.request.id,
                "task_args": args,
                "task_kwargs": kwargs,
            },
        )
        return super().__call__(*args, **kwargs)

    def on_success(self, retval, task_id, args, kwargs):
        self.logger.info(
            "Задача выполнена успешно",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "result": retval,
            },
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.logger.error(
            "Ошибка выполнения задачи",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "task_args": args,
                "task_kwargs": kwargs,
                "exception": str(exc),
                "traceback": str(einfo),
            },
        )

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        self.logger.warning(
            "Попытка повторной выполнения задачи",
            extra={
                "task_name": self.name,
                "task_id": task_id,
                "task_args": args,
                "task_kwargs": kwargs,
                "exception": str(exc),
                "traceback": str(einfo),
            },
        )

celery_app.Task = CeleryTaskWithLogging