from typing import Annotated

from fastapi import Depends
from core.database import database
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis_client import get_redis

SessionDep = Annotated[AsyncSession, Depends(database.get_session)]

RedisDep = Annotated[Redis, Depends(get_redis)]