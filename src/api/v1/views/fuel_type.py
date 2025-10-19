from fastapi import APIRouter, Depends, HTTPException

from api.v1.schemas.fuel_type import (
    FuelTypeCreateSchema, 
    FuelTypeUpdateSchema,
    FuelTypeListRequestSchema,
    FuelTypeListResponseSchema,
    FuelTypeResponseSchema
)
from logic.fuel_type import (
    create_fuel_type as create_fuel_type_logic,
    get_fuel_types_list as get_fuel_types_list_logic,
    get_fuel_type as get_fuel_type_logic,
    update_fuel_type as update_fuel_type_logic,
    get_fuel_type_by_name as get_fuel_type_by_name_logic
)
from dependencies.repo_factory import FactoryDep


router = APIRouter(prefix='/fuel-type', tags=['Fuel Type'])


@router.post('/', response_model=FuelTypeResponseSchema)
async def create_fuel_type(
    factory: FactoryDep,
    data: FuelTypeCreateSchema
):
    instance = await create_fuel_type_logic(
        repo=factory.get_fuel_type_repository(),
        name=data.name,
        display_name=data.display_name,
        icon_url=data.icon_url
    )
    
    return {"data": instance}
    
    
@router.patch('/{fuel_type_id}', response_model=FuelTypeResponseSchema)
async def update_fuel_type(
    factory: FactoryDep,
    fuel_type_id: int,
    data: FuelTypeUpdateSchema
):
    instance = await get_fuel_type_logic(
        repo=factory.get_fuel_type_repository(),
        fuel_type_id=fuel_type_id
    )
    
    if not instance:
        raise HTTPException(status_code=404, detail='Fuel type not found')
    
    updated_instance = await update_fuel_type_logic(
        repo=factory.get_fuel_type_repository(),
        instance=instance,
        **data.model_dump(exclude_unset=True)
    )
    
    return {"data": updated_instance}


@router.get('/{fuel_type_id}', response_model=FuelTypeResponseSchema)
async def get_fuel_type(
    factory: FactoryDep,
    fuel_type_id: int
):
    instance = await get_fuel_type_logic(
        repo=factory.get_fuel_type_repository(),
        fuel_type_id=fuel_type_id
    )
    return {"data": instance}


@router.get('/', response_model=FuelTypeListResponseSchema)
async def get_fuel_types_list(
    factory: FactoryDep,
    query_params: FuelTypeListRequestSchema = Depends()
):
    data = await get_fuel_types_list_logic(
        repo=factory.get_fuel_type_repository(),
        **query_params.model_dump(exclude_unset=True)
    )
    
    return {
        "data": {
            "limit": query_params.limit,
            "offset": query_params.offset,
            "records": data,
            "count": 0,
        }
    }
    
    

