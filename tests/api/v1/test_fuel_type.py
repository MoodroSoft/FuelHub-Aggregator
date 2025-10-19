import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status as http_status

from models import FuelType

pytestmark = pytest.mark.anyio


async def test_list_fuel_types(
    client: AsyncClient,
    create_fuel_types,
):
    """
    Тест для получения списка видов топлива.
    Проверяет, что API возвращает корректный список созданных объектов.
    """
    # Выполняем запрос к API
    response = await client.get("/api/v1/fuel-type/")

    # Проверяем статус-код
    assert response.status_code == http_status.HTTP_200_OK

    # Проверяем, что в ответе пришел список
    response_data = response.json()['data']['records']
    assert isinstance(response_data, list)

    # Проверяем количество элементов
    assert len(response_data) == len(create_fuel_types)

    # Проверяем, что данные соответствуют фикстурам
    assert response_data[0]["name"] == create_fuel_types[0].name
