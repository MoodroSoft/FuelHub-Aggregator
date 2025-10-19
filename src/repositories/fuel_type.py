from typing import Any, List, Optional, Sequence, Tuple, Type

from sqlalchemy import Delete, Select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models import FuelType
from core.repositories import BaseRepository, NotNullableFieldException


class FuelTypeRepository(BaseRepository[FuelType]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, FuelType)
        
    def search_query(
        self,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        fuel_type_id: Optional[int] = None,
        **extra_options
    ) -> Select[Tuple[FuelType]]:
        query = self.query()
        
        if fuel_type_id is not None:
            query = query.where(FuelType.id == fuel_type_id)
        
        if name is not None:
            query = query.where(FuelType.name.ilike(f"%{name}%"))
        
        if display_name is not None:
            query = query.where(FuelType.display_name.ilike(f"%{display_name}%"))
        
        if is_active is not None:
            query = query.where(FuelType.is_active.is_(is_active))
            
        loading_columns = extra_options.get("load_only", [])
        if loading_columns:
            query = self._load_only(query, *loading_columns)

        return query
    
    async def create(
        self,
        name: str,
        display_name: str,
        icon_url: Optional[str] = None,
        is_active: bool = True
    ):
        model = FuelType(
            name=name,
            display_name=display_name,
            icon_url=icon_url,
            is_active=is_active
        )
        self.session.add(model)
                
        return model
    
    async def update(
        self,
        instance: FuelType,
        **update_data: Any
    ):
        self._validate_fields(*update_data.keys())
        
        not_nullable_fields = self._not_nullable_fields()
        
        for key, value in update_data.items():
            if key in not_nullable_fields and value is None:
                raise NotNullableFieldException(self.model, key)

            setattr(instance, key, value)
        
        self.session.add(instance)
        
        return instance

    async def get(
        self,
        fuel_type_id: int,
        **extra_options
    ) -> Optional[FuelType]:
        smtpd = self.search_query(
            fuel_type_id=fuel_type_id,
            **extra_options
        )
        return await self._fetch_one(smtpd)

    async def get_by_name(
        self,
        name: str,
        **extra_options
    ) -> Optional[FuelType]:
        smtpd = self.search_query(
            name=name,
            **extra_options
        )
        return await self._fetch_one(smtpd)
    
    async def delete(self, fuel_type_id: int) -> None:
        stmtd: Delete = delete(FuelType).where(FuelType.id == fuel_type_id)
        await self.session.execute(stmtd)
        
    async def get_list(
        self, 
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
        **extra_options
    ) -> Sequence[FuelType]:
        smtpd = self.search_query(
            name=name,
            display_name=display_name,
            is_active=is_active,
            **extra_options
        )
        
        return await self._do_paginate_query(smtpd, limit, offset)