from contextlib import asynccontextmanager

# import sentry_sdk
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from src.api.routers import main_router
from src.core.config import jaeger_settings, project_settings, redis_settings

# , sentry_settings
from src.core.jaeger import configure_tracer
from src.core.logger import request_id_var
from src.db.init_postgres import create_first_superuser
from src.db.postgres import create_database
from src.db.rabbitmq import rabbitmq_producer
from src.db.redis_cache import RedisCacheManager, RedisClientFactory

from fastapi import FastAPI, Request, status

# sentry_sdk.init(dsn=sentry_settings.dsn, traces_sample_rate=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis_cache_manager = RedisCacheManager(redis_settings)
        redis_client = await RedisClientFactory.create(redis_settings.dsn)

        await create_database(redis_client)
        await create_first_superuser()
        await redis_cache_manager.setup()
        await rabbitmq_producer.setup()
        yield
    except Exception:
        import traceback

        traceback.print_exc()
        raise
    finally:
        await redis_cache_manager.tear_down()
        await rabbitmq_producer.close()


app = FastAPI(
    title=project_settings.project_auth_name,
    docs_url="/auth/openapi",
    openapi_url="/auth/openapi.json",
    default_response_class=ORJSONResponse,
    summary=project_settings.project_auth_summary,
    version=project_settings.project_auth_version,
    terms_of_service=project_settings.project_auth_terms_of_service,
    openapi_tags=project_settings.project_auth_tags,
    lifespan=lifespan,
)

app.include_router(main_router)

if jaeger_settings.debug:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)


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
