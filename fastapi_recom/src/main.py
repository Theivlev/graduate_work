from contextlib import asynccontextmanager

from fastapi.responses import ORJSONResponse
from src.api.routers import main_router
from src.core.config import project_settings, redis_settings
from src.core.logger import request_id_var
from src.db.redis_cache import RedisCacheManager
from src.rabbitmq.broker import broker
from src.rabbitmq.app import app_broker
from fastapi import FastAPI, Request, status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление ресурсами FastAPI."""

    redis_cache_manager = RedisCacheManager(redis_settings)
    try:
        await redis_cache_manager.setup()
        await app_broker.start()
        yield

    finally:
        await redis_cache_manager.tear_down()
        await app_broker.close()


app = FastAPI(
    title=project_settings.name,
    docs_url="/recom/openapi",
    openapi_url="/recom/openapi.json",
    default_response_class=ORJSONResponse,
    summary=project_settings.summary,
    version=project_settings.version,
    terms_of_service=project_settings.terms_of_service,
    openapi_tags=project_settings.tags,
    lifespan=lifespan,
)

app.include_router(main_router)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    request_id_var.set(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response
    finally:
        request_id_var.set(None)
