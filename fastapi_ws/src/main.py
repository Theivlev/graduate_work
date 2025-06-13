import logging
from contextlib import asynccontextmanager

import aio_pika
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from src.api.routers import main_router
from src.core.config import project_settings, rabbit_settings, redis_settings, ws_settings
from src.db.postgres import create_database
from src.db.redis_cache import RedisCacheManager, RedisClientFactory
from src.services.consumers import on_ws_message
from src.services.superuser_service import create_superuser

from fastapi import FastAPI, Request, status

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_cache_manager = RedisCacheManager(redis_settings)
    redis_client = await RedisClientFactory.create(redis_settings.dsn)
    await create_database(redis_client)
    await redis_cache_manager.setup()
    superuser = await create_superuser()
    if superuser and superuser.api_key:
        logger.info(f"Шифрованный ключ для авторизации суперпользователем: {superuser.api_key}")
    connection = await aio_pika.connect_robust(
        login=rabbit_settings.user,
        password=rabbit_settings.password,
        host=rabbit_settings.host,
        port=rabbit_settings.port,
        virtualhost="/",
    )
    channel = await connection.channel()
    ws_queue = await channel.get_queue(ws_settings.ws_queue)
    await ws_queue.consume(lambda msg: on_ws_message(msg, channel))
    logger.info("Начало работы сервиса Вебсокет")

    try:
        yield
    finally:
        await connection.close()
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
