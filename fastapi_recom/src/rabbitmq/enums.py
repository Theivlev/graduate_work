from enum import StrEnum


class RoutingKeys(StrEnum):
    ACTIONS = 'actions'
    RECOMMENDATIONS = "recommendations"


class ExchangeType(StrEnum):
    DIRECT = 'direct'
    FANOUT = 'fanout'
    TOPIC = 'topic'
