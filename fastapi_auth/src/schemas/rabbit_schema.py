from pydantic import BaseModel


class WsMessage(BaseModel):
    """Схема авторизации по сообщению из брокера."""

    email: str
    fullname: str
    event_type: str = "user_verified"
