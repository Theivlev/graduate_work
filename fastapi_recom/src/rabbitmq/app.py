from faststream import FastStream
from .broker import broker
from src.rabbitmq.consumer.actions_consumer import actions_user  # noqa


app_broker = FastStream(broker)
