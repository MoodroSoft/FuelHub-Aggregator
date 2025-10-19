from typing import Optional
from pydantic import BaseModel, Field

from core.schemas.base import OrmBaseModel
from core.schemas.base import BaseResponseSchema
from core.schemas.base_request_schemas import BasePaginationRequestSchema
from core.schemas.base_response_schemas import BasePaginationResponseSchema


# Request schemas

class FuelTypeListRequestSchema(BasePaginationRequestSchema):
    name: Optional[str] = Field(default=None)
    display_name: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    

class FuelTypeCreateSchema(BaseModel):
    name: str
    display_name: str
    icon_url: str
    

class FuelTypeUpdateSchema(BaseModel):
    name: Optional[str]
    display_name: Optional[str]
    icon_url: Optional[str]
    is_active: Optional[bool]
    
    
# Response schemas

class FuelTypeDataSchema(OrmBaseModel):
    name: str
    display_name: str
    icon_url: Optional[str] = Field(default=None)
    
    
class FuelTypeListDataSchema(BasePaginationResponseSchema):
    records: list[FuelTypeDataSchema]
    
    
class FuelTypeResponseSchema(BaseResponseSchema):
    data: FuelTypeDataSchema    # type: ignore
    
    
class FuelTypeListResponseSchema(BaseResponseSchema):
    data: FuelTypeListDataSchema    # type: ignore