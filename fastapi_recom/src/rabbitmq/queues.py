from faststream.rabbit import RabbitQueue

from .enums import RoutingKeys
from .dlq import DLX_EXCHANGE_NAME, DLQ_ROUTING_KEYS


QUEUES = {
    RoutingKeys.ACTIONS: RabbitQueue(
        name=RoutingKeys.ACTIONS.value,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DLX_EXCHANGE_NAME,
            "x-dead-letter-routing-key": DLQ_ROUTING_KEYS[RoutingKeys.ACTIONS],
        }
    ),
    RoutingKeys.RECOMMENDATIONS: RabbitQueue(
        name=RoutingKeys.RECOMMENDATIONS.value,
        durable=True,
    ),
}
