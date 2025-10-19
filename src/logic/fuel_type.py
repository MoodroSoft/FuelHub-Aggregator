from typing import Any, Optional
from models import FuelType
from repositories.fuel_type import FuelTypeRepository


async def create_fuel_type(
    repo: FuelTypeRepository,
    name: str,
    display_name: str,
    icon_url: Optional[str] = None,
    is_active: bool = True
):
    return await repo.create(
        name=name,
        display_name=display_name,
        icon_url=icon_url,
        is_active=is_active
    )


async def update_fuel_type(
    repo: FuelTypeRepository,
    instance: FuelType,
    **update_data: Any
):
    return await repo.update(
        instance=instance,
        **update_data
    )


async def get_fuel_type(
    repo: FuelTypeRepository,
    fuel_type_id: int
):
    return await repo.get(
        fuel_type_id=fuel_type_id
    )


async def get_fuel_type_by_name(
    repo: FuelTypeRepository,
    name: str
):
    return await repo.get_by_name(
        name=name
    )


async def get_fuel_types_list(
    repo: FuelTypeRepository,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
    order: str = 'id',
    ascending: bool = True
):
    return await repo.get_list(
        name=name,
        display_name=display_name,
        is_active=is_active,
        limit=limit,
        offset=offset,
        order=order,
        ascending=ascending
    )
    