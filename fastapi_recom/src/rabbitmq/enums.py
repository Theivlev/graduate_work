from enum import StrEnum


class RoutingKeys(StrEnum):
    ACTIONS = 'actions'


class ExchangeType(StrEnum):
    DIRECT = 'direct'
    FANOUT = 'fanout'
    TOPIC = 'topic'
