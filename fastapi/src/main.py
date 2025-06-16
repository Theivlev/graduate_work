from contextlib import asynccontextmanager

import sentry_sdk
from elasticsearch import AsyncElasticsearch
from fastapi.responses import ORJSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from src.api.routers import main_router
from src.core.config import elastic_settings, jaeger_settings, project_settings, redis_settings, sentry_settings
from src.core.jaeger import configure_tracer
from src.core.logger import request_id_var
from src.db.elastic_dao import ElasticDAO
from src.db.redis_cache import RedisCacheManager

from fastapi import FastAPI, Request, status

sentry_sdk.init(dsn=sentry_settings.dsn, traces_sample_rate=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление ресурсами FastAPI."""

    elastic_client = None
    redis_cache_manager = RedisCacheManager(redis_settings)
    try:
        await redis_cache_manager.setup()

        elastic_client = AsyncElasticsearch(hosts=[elastic_settings.dsn])
        app.state.elastic = ElasticDAO(elastic_client)

        yield

    finally:
        await redis_cache_manager.tear_down()

        if elastic_client:
            await elastic_client.close()


app = FastAPI(
    title=project_settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    summary=project_settings.project_summary,
    version=project_settings.project_version,
    terms_of_service=project_settings.project_terms_of_service,
    openapi_tags=project_settings.project_tags,
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
