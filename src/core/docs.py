from fastapi import APIRouter, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse

from core.config import settings


def init_app(app: FastAPI):
    router = APIRouter()

    @router.get('/openapi.json', include_in_schema=False)
    async def get_open_api_endpoint():
        openapi = get_openapi(
            title=app.title,
            version=settings.DOCS_API_VERSION,
            routes=app.routes,
            servers=[{'url': app.root_path}] if app.root_path else None,
        )

        return ORJSONResponse(openapi)

    @router.get('/swagger/', include_in_schema=False)
    async def swagger_ui_html():
        return get_swagger_ui_html(
            # openapi_url=app.root_path + '/openapi.json',
            openapi_url=app.root_path + '/openapi.json',
            title=app.title + ' - Swagger UI',
            swagger_ui_parameters={
                "defaultModelsExpandDepth": 0,  # This collapses the Schemas section, set -1 to disable
                "docExpansion": "list",  # Expands only the endpoints list while collapsing schemas
            }
        )

    app.include_router(router)