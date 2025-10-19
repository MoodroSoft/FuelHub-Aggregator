from fastapi import APIRouter

from api.v1.views.fuel_type import router as fuel_type_router


router = APIRouter(prefix="/v1")

router.include_router(fuel_type_router)


