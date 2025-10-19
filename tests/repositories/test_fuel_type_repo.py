import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.fuel_type import FuelTypeRepository
from models import FuelType

pytestmark = pytest.mark.anyio


async def test_repo_list_fuel_types(
    session: AsyncSession,
    create_fuel_types: list[FuelType],
):
    """
    Тест для метода list репозитория видов топлива.
    Проверяет, что репозиторий возвращает список объектов из базы данных.
    """
    # Создаем экземпляр репозитория
    repo = FuelTypeRepository(session)

    # Получаем список объектов
    result = await repo.get_list()

    # Проверяем, что результат - это список
    assert isinstance(result, list)
    # Проверяем количество
    assert len(result) == len(create_fuel_types)
    # Проверяем тип первого элемента
    assert isinstance(result[0], FuelType)
    # Проверяем соответствие данных
    assert result[0].name == create_fuel_types[0].name
