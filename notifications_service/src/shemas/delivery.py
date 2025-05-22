from src.models.dto import AbstractDTO


class DeliveryDTO(AbstractDTO):
    notification: str
    data_store: dict
