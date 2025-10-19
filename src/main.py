from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from core.config import settings
from core import docs
from core.middlewares import LoggingMiddleware
from api.v1.router import router as v1_router


app = FastAPI(
    title="FuelHub Aggregator",
    openapi_url=None,
    version="0.0.1",
    root_path=settings.ROOT_PATH,
    default_response_class=ORJSONResponse,
    root_path_in_servers=True,
    servers=[{"url": "/v1", "description": "V1"}],
)

docs.init_app(app)


# Подключение роутеров
app.include_router(v1_router)


# Подключение middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGIN_LIST,
    allow_credentials=True,
    allow_methods=("GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"),
    allow_headers=(
        "Access-Control-Allow-Origin",
        "X-Requested-With",
        "Authorization",
        "Content-Disposition",
    ),
    expose_headers=("Authorization", "Content-Disposition"),
)

app.add_middleware(LoggingMiddleware)
