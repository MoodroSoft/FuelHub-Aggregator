from datetime import datetime
from typing import Optional

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator

from core.config import settings


class BasePaginationRequestSchema(BaseModel):
    limit: int = Field(Query(
        default=settings.TABLE_DEFAULT_PAGINATION_LIMIT,
        description="Лимит записей",
    ))
    offset: int = Field(Query(
        default=settings.TABLE_DEFAULT_PAGINATION_OFFSET,
        description="Смещение записей",
    ))
    order: str = Field(Query(
        default=settings.TABLE_DEFAULT_PAGINATION_ORDER,
        description="Сортировка по столбцу",
    ))
    ascending: bool = Field(Query(
        default=settings.TABLE_DEFAULT_PAGINATION_ASCENDING,
        description="Сортировать в порядке возрастания или убывания",
    ))

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, value):
        """Done this way because Pydantic ge amd gt is not validated as RequestValidationError"""
        if value <= 0:
            message = "'limit' field must be greater than 0"
            raise RequestValidationError(
                [
                    {
                        "loc": ("query", "limit"),
                        "msg": message,
                        "type": "value_error"
                    }
                ]
            )

        return value

    @field_validator('offset')
    @classmethod
    def validate_offset(cls, value):
        if value < 0:
            message = "'offset' field must be greater or equal than 0"
            raise RequestValidationError(
                [
                    {
                        "loc": ("query", "offset"),
                        "msg": message,
                        "type": "value_error"
                    }
                ]
            )

        return value
