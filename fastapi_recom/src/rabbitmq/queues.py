from faststream.rabbit import RabbitQueue

from .dlq import DLQ_ROUTING_KEYS, DLX_EXCHANGE_NAME
from .enums import RoutingKeys

QUEUES = {
    RoutingKeys.ACTIONS: RabbitQueue(
        name=RoutingKeys.ACTIONS.value,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DLX_EXCHANGE_NAME,
            "x-dead-letter-routing-key": DLQ_ROUTING_KEYS[RoutingKeys.ACTIONS],
        },
    ),
    RoutingKeys.RECOMMENDATIONS: RabbitQueue(
        name=RoutingKeys.RECOMMENDATIONS.value,
        durable=True,
    ),
}
