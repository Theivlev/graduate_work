from faststream import FastStream
from src.rabbitmq.consumer.actions_consumer import actions_user  # noqa

from .broker import broker

app_broker = FastStream(broker)
