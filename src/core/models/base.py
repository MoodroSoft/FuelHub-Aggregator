from typing import TypeVar
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, func


metadata_obj = MetaData()


class Base(DeclarativeBase):
    metadata = metadata_obj
    
    
class MixinModel(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


SQLAlchemyModel = TypeVar("SQLAlchemyModel", bound=Base)
