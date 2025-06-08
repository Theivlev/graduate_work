from rabbitmq.queues import QUEUES
from rabbitmq.exchanges import EXCHANGES
from rabbitmq.enums import RoutingKeys
from rabbitmq.broker import broker
from ...shemas.actions_user import ActionsUserDTO


@broker.subscriber(QUEUES[RoutingKeys.ACTIONS], EXCHANGES[RoutingKeys.ACTIONS])
async def actions_user(message: ActionsUserDTO):
    pass
