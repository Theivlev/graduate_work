from faststream.rabbit import RabbitExchange

from .enums import ExchangeType, RoutingKeys


EXCHANGES = {
    RoutingKeys.ACTIONS: RabbitExchange(
        name=RoutingKeys.ACTIONS.value,
        type=ExchangeType.DIRECT,
        durable=True
    ),
}
