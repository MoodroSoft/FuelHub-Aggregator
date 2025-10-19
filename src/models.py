from typing import Optional
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base




class FuelType(Base):
    __tablename__ = "fuel_types"
    
    __table_args__ = (
        Index("fuel_types_name_idx", "name", unique=True),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str]
    display_name : Mapped[str]
    icon_url : Mapped[Optional[str]]
    is_active : Mapped[bool] = mapped_column(default=True)