import enum
from typing import Any, List
from pydantic import BaseModel, Field


class OrmBaseModel(BaseModel):

    class Config:
        from_attributes = True
        
        
class ResponseStatusEnum(str, enum.Enum):
    """Contains status for response"""
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    WARNING = 'WARNING'


class BaseResponseSchema(BaseModel):
    """Base response schema"""
    status: ResponseStatusEnum = Field(
        default=ResponseStatusEnum.SUCCESS,
        description="Статус ответа",
        examples=[ResponseStatusEnum.SUCCESS],
    )
    data: List[Any] | Any | dict | None = Field(
        default=None,
        description="Результат запроса",
    )
    message: str | None = Field(
        default="Successful response",
        description="Пользовательское сообщение",
        examples=["Successful response"],
    )
    system_message: str | None = Field(
        default="success_response",
        description="Системное сообщение",
        examples=["success_response"],
    )
