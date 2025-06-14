import aio_pika
from aio_pika.abc import AbstractRobustChannel
from fastapi import FastAPI

from src.core.config import rabbit_mq_settings

rabbitmq_channel: AbstractRobustChannel | None = None


async def setup_rabbitmq(app: FastAPI):
    app.state.rabbit_connection = await aio_pika.connect_robust(
        login=rabbit_mq_settings.user,
        password=rabbit_mq_settings.password,
        host=rabbit_mq_settings.host,
        port=rabbit_mq_settings.port,
        virtual_host="/",
    )
    app.state.rabbit_channel = await app.state.rabbit_connection.channel()
    global rabbitmq_channel
    rabbitmq_channel = app.state.rabbit_channel


def get_rabbitmq_channel():
    if rabbitmq_channel:
        return rabbitmq_channel
    else:
        raise Exception("RabbitMQ channel not initialized")


async def close_rabbitmq(app: FastAPI):
    if hasattr(app.state, "rabbit_connection"):
        await app.state.rabbit_connection.close()
