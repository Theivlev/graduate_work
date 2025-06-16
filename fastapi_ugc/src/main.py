from contextlib import asynccontextmanager

import sentry_sdk
from broker.kafka import kafka_producer
from broker.rabbit import close_rabbitmq, setup_rabbitmq
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from src.api.routers import main_router
from src.core.config import mongo_settings, project_settings, sentry_settings
from src.core.logger import request_id_var
from src.db.mongo import init_db

from fastapi import FastAPI, Request, status  # noqa

sentry_sdk.init(dsn=sentry_settings.dsn, traces_sample_rate=1.0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = AsyncIOMotorClient(str(mongo_settings.ugc_dsn))
    app.state.db = app.state.client[mongo_settings.ugc_db]
    await setup_rabbitmq(app)
    await init_db(app.state.db)
    await kafka_producer.start()
    try:
        yield
    finally:
        app.state.client.close()
        await close_rabbitmq(app)
        await kafka_producer.stop()


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
