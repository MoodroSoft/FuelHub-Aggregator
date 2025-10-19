from typing import Annotated
from fastapi import Depends
from repositories import fuel_type

from .dependencies import SessionDep


class RepositoryFactory:
    def __init__(self, db_session: SessionDep):
        self.db_session = db_session

    def get_fuel_type_repository(self) -> fuel_type.FuelTypeRepository:
        return fuel_type.FuelTypeRepository(self.db_session)


FactoryDep = Annotated[RepositoryFactory, Depends(RepositoryFactory)]