from contextlib import asynccontextmanager

from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from src.api.routers import main_router
from src.core.config import project_settings, redis_settings
from src.db.postgres import create_database
from src.db.redis_cache import RedisCacheManager, RedisClientFactory

from fastapi import FastAPI, Request, status


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cache_manager = RedisCacheManager(redis_settings)
    redis_client = await RedisClientFactory.create(redis_settings.dsn)
    try:
        await create_database(redis_client)
        await redis_cache_manager.setup()
        yield
    finally:
        await redis_cache_manager.tear_down()


app = FastAPI(
    title=project_settings.name,
    docs_url="/ws/openapi",
    openapi_url="/ws/openapi.json",
    default_response_class=ORJSONResponse,
    summary=project_settings.summary,
    version=project_settings.version,
    terms_of_service=project_settings.terms_of_service,
    openapi_tags=project_settings.tags,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=project_settings.static_path), name="static")
app.include_router(main_router)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    return response
