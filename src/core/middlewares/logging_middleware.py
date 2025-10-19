import json
import logging
import traceback
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger("app.middleware")
logger.setLevel(logging.INFO)


def mask_token(token: str | None) -> str | None:
    """Маскировка токена авторизации."""
    if not token:
        return None
    return token[:4] + "****" + token[-4:] if len(token) > 8 else "****"


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов и обработки ошибок."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        accept_language = request.headers.get("accept-language")
        method = request.method
        path = request.url.path
        auth_header = request.headers.get("authorization")
        masked_auth = mask_token(auth_header)

        # Базовый лог запроса
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "client_ip": client_ip,
                    "user_agent": user_agent,
                    "accept_language": accept_language,
                    "method": method,
                    "path": path,
                    "auth_token": masked_auth,
                },
                ensure_ascii=False,
            )
        )

        try:
            response = await call_next(request)
            return response

        except StarletteHTTPException as exc:
            # Ошибки HTTP уровня
            body = await self._get_request_body(request)
            log = {
                "request_id": request_id,
                "error": str(exc.detail),
                "status_code": exc.status_code,
                "body": body,
            }
            logger.error(json.dumps(log, ensure_ascii=False))
            return ORJSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "request_id": request_id},
            )

        except RequestValidationError as exc:
            # Ошибки валидации
            body = await self._get_request_body(request)
            log = {
                "request_id": request_id,
                "error": "Request validation error",
                "status_code": HTTP_422_UNPROCESSABLE_ENTITY,
                "body": body,
                "errors": exc.errors(),
            }
            logger.error(json.dumps(log, ensure_ascii=False))
            return ORJSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": exc.errors(), "request_id": request_id},
            )

        except Exception as exc:
            # Необработанные ошибки
            body = await self._get_request_body(request)
            log = {
                "request_id": request_id,
                "error": repr(exc),
                "status_code": HTTP_500_INTERNAL_SERVER_ERROR,
                "body": body,
                "traceback": traceback.format_exc(),
            }
            logger.error(json.dumps(log, ensure_ascii=False))
            return ORJSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal Server Error", "request_id": request_id},
            )

    async def _get_request_body(self, request: Request) -> str | None:
        """Читает тело запроса для логирования (только для ошибок)."""
        try:
            body = await request.body()
            if not body:
                return None
            return body.decode("utf-8", errors="ignore")
        except Exception:
            return None