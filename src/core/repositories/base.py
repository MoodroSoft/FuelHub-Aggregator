import abc
from typing import Any, Generic, Sequence, Tuple, Type, TypeVar

from httpx import get
from sqlalchemy import Select, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only


from core.models.base import Base
from core.repositories.exceptions import InvalidFieldException

T = TypeVar("T", bound=Base)

class BaseRepository(abc.ABC, Generic[T]):
    
    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self.session = session
        self.model = model
        
    def query(self) -> Select[Tuple[T]]:
        return select(self.model)
    
    async def refresh(self, obj: T) -> T:
        await self.session.refresh(obj)
        return obj
    
    async def commit(self) -> None:
        await self.session.commit()
        
    async def rollback(self) -> None:
        await self.session.rollback()
        
    async def flush(self, objects: Sequence[Any] | None = None) -> None:
        await self.session.flush(objects=objects)


    def _validate_fields(self, *fields: str) -> None:
        """
        Проверка наличия полей в модели.
        
        Args:
            fields (str): Названия полей для проверки.
            model (SQLAlchemyModel): Модель для проверки. По умолчанию используется модель репозитория.

        Raises:
            InvalidFieldException: если модель не содержит указанных полей.
        """
        
        mapper = inspect(self.model)
        
        invalid_fields: set[str] = set(fields) - set(mapper.all_orm_descriptors.keys())
        
        if invalid_fields:
            raise InvalidFieldException(self.model, *invalid_fields)
        
    def _not_nullable_fields(self) -> set[str]:
        """
        Получение обязательных полей модели.
        
        Returns:
            set[str]: Названия обязательных полей.
        """
        mapper = inspect(self.model)
        
        fields: set[str] = {column for column in mapper.all_orm_descriptors.keys() if not mapper.columns[column].nullable}
        
        return fields
    
    def _load_only(self, query: Select[Any], *fields: str) -> Select[Tuple[T]]:
        """
        Загрузка только указанных полей.
        
        Args:
            fields (str): Названия полей для загрузки.
            
        Returns:
            Select[Tuple[SQLAlchemyModel]]: Запрос для выполнения.
        """
        self._validate_fields(*fields)
        
        model_fields = [getattr(self.model, field) for field in fields]
        
        return query.options(load_only(*model_fields))
        
    async def _fetch_one(self, query: Select[Any]) -> T | None:
        """
        Получение одного объекта из базы данных.

        Args:
            query (Select[Any]): Запрос для выполнения.

        Returns:
            SQLAlchemyModel | None: Найденный объект или None, если объект не найден.
        """
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def _fetch_many(self, query: Select[Any]) -> Sequence[T]:
        """
        Получение списка объектов из базы данных.

        Args:
            query (Select): Запрос для выполнения.

        Returns:
            Sequence[SQLAlchemyModel]: Список найденных объектов.
        """
        result = await self.session.execute(query)
        return result.unique().scalars().all()
    
    async def _do_paginate_query(self, smtpd: Select[Any], limit: int, offset: int) -> Sequence[T]:
        """
        Выполнение пагинации запроса.
        
        Args:
            smtpd (Select[Any]): Запрос для выполнения.
            
        Returns:
            Sequence[SQLAlchemyModel]: Список найденных объектов.
        """
        return await self._fetch_many(smtpd.limit(limit).offset(offset))