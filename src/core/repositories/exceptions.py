from typing import Type

from core.models import SQLAlchemyModel


class InvalidFieldException(Exception):
    def __init__(self, model: Type[SQLAlchemyModel], *fields: str) -> None:
        self.model = model
        self.fields = fields
        
        fields_to_msg = "', '".join(fields)
        message = f"Invalid field ['{fields_to_msg}'] for model '{self.model.__name__}'"
        
        super().__init__(message)


class NotNullableFieldException(Exception):
    def __init__(self, model: Type[SQLAlchemyModel], field: str) -> None:
        self.model = model
        self.fields = field
        
        message = f"Non-nullable field '{field}' for model '{self.model.__name__}' containts null values"
        
        super().__init__(message)