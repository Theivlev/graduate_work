from faststream import FastStream
from .broker import broker
from rabbitmq.consumer.actions_consumer import actions_user  # noqa


app = FastStream(broker)
