from typing import List, Any

from pydantic import BaseModel, Field


class BasePaginationResponseSchema(BaseModel):
    limit: int = Field(description="Лимит записей")
    offset: int = Field(description="Смещение записей")
    count: int = Field(description="Количество записей")
    records: List[Any] = Field(description="Список записей")
