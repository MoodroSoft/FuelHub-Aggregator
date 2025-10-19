from typing import List, Literal, Union
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DEBUG: bool = True
    
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fha_local"
    POSTGRES_USER: str = "fha_local"
    POSTGRES_PASSWORD: str = "fha_local"
    DB_ECHO: bool = False

    PG_BOUNCER_HOST: str = "pgbouncer"
    PG_BOUNCER_PORT: int = 6432

    DB_SECRET_KEY: str = "WpgipwMqgABLXu6fThnoLv0bMD9vnq5Aj2MmgDqQGBwBvDWc0rhXDu5sKWYRmTg3qNBXMqvEy8QgEG9y"
    
    SECRET_KEY: str = "@kep7aEb0MNh7iaEcD@bJodfubeW^Pr2eWt0oG~J_aD93o+7ReokX>Q7h.82>0yErn?nk5!LxDo-M"

    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 10  # 10 минут
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 14  # 14 дней
    JWT_ALGORITHM: str = "HS256"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRE_SECONDS: int = 300

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_DEFAULT_USER: str = "fha_local"
    RABBITMQ_DEFAULT_PASS: str = "fha_local"
    RABBITMQ_DEFAULT_VHOST: str = "/"
    
    ROOT_PATH: str = "/api"
    DOCS_API_VERSION: str = "0.0.1"
    
    TABLE_DEFAULT_PAGINATION_LIMIT: int = 20
    TABLE_DEFAULT_PAGINATION_OFFSET: int = 0
    TABLE_DEFAULT_PAGINATION_ORDER: str = "id"
    TABLE_DEFAULT_PAGINATION_ASCENDING: bool = False
    
    CORS_ORIGIN_LIST: Union[List[str], str] = ['http://127.0.0.1:5173']
    COOKIE_SAMESITE: Literal['lax', 'strict', 'none'] = "none"
    SSL_ENABLED: bool = True
    
    PUBLIC_URL: str = 'http://127.0.0.1:8000'
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://" \
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@" \
            f"{self.PG_BOUNCER_HOST}:{self.PG_BOUNCER_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()