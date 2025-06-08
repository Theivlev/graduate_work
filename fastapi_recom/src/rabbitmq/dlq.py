from .enums import RoutingKeys


DLX_EXCHANGE_NAME = "dlx_exchange"
DLQ_QUEUE_NAME = "dead_letter_queue"

DLQ_ROUTING_KEYS = {
    RoutingKeys.ACTIONS: "actions_dl",
}
