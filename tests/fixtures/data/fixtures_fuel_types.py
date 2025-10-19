import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models import FuelType

pytestmark = pytest.mark.anyio


@pytest.fixture()
async def create_fuel_types(session: AsyncSession):
    fuel_types = [
        FuelType(
            name="Бензин АИ-95",
            display_name="АИ-95",
            icon_url="/storage/icons/95.png",
            is_active=True
        ),
        FuelType(
            name="Бензин АИ-98",
            display_name="АИ-98",
            icon_url="/storage/icons/98.png",
            is_active=True
        ),
        FuelType(
            name="ДТ",
            display_name="ДТ",
            icon_url="/storage/icons/dt.png",
            is_active=True
        ),
    ]
    
    session.add_all(fuel_types)
    await session.commit()
    
    yield fuel_types