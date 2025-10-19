from redis.asyncio import Redis, ConnectionPool
from core.config import settings


redis_pool = ConnectionPool.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    decode_responses=True,
    max_connections=100,
)


def get_redis() -> Redis:
    return Redis(connection_pool=redis_pool)