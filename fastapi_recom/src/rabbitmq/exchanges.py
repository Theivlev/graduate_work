from faststream.rabbit import RabbitExchange

from .enums import RoutingKeys, StrEnum


class ExchangeType(str, StrEnum):
    DIRECT = 'direct'
    FANOUT = 'fanout'
    TOPIC = 'topic'


EXCHANGES = {
    RoutingKeys.ACTIONS: RabbitExchange(
        name=RoutingKeys.ACTIONS.value,
        type=ExchangeType.DIRECT,
        durable=True
    ),
}
