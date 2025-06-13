from contextlib import asynccontextmanager

from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from src.api.routers import main_router
from src.core.config import mongo_settings, project_settings
from src.core.logger import request_id_var
from src.db.mongo import init_db

from fastapi import FastAPI, Request, status  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = AsyncIOMotorClient(str(mongo_settings.ugc_dsn))
    app.state.db = app.state.client[mongo_settings.ugc_db]

    await init_db(app.state.db)
    try:
        yield
    finally:
        await app.state.client.close()


app = FastAPI(
    title=project_settings.name,
    docs_url="/social/openapi",
    openapi_url="/social/openapi.json",
    default_response_class=ORJSONResponse,
    summary=project_settings.summary,
    version=project_settings.version,
    terms_of_service=project_settings.terms_of_service,
    openapi_tags=project_settings.tags,
    lifespan=lifespan,
)

app.include_router(main_router)
