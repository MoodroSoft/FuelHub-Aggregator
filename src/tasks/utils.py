import asyncio
from functools import wraps
import logging
from typing import Callable

from fastapi.concurrency import run_in_threadpool
from celery.exceptions import CeleryError
from kombu.exceptions import KombuError


logger = logging.getLogger(__name__)


def async_task(func):
    """
    Превращение задач Celery в асмнхронные.
    """

    @wraps(func)
    def wrapped(self, *args, **kwargs) -> None:
        asyncio.get_event_loop().run_until_complete(func(self, *args, **kwargs))

    return wrapped


async def run_task_in_threadpool(task: Callable, *args, **kwargs):
    """
    Запуск Celery тасок в threadpool для предотвращения блокировки event_loop.

    # ------ Примеры запуска ------ #

    from tasks import some_task

    await run_task_in_threadpool(some_task.delay)

    """

    try:
        return await run_in_threadpool(task, *args, **kwargs)
    except (CeleryError, KombuError):
        logger.exception(
            f"Ошибка при запуске таски {task.__name__}, {args=}, {kwargs=}"
        )
