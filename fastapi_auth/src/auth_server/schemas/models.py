from typing import Dict, List

from pydantic import BaseModel, Field


class CheckTokenResult(BaseModel):
    is_valid: bool
    user_id: str | None
    error_message: str | None
    is_subscribed: bool = False
    roles: List[str] = Field(default_factory=list)

    def to_proto(self) -> Dict:
        return {
            "is_valid": self.is_valid,
            "user_id": self.user_id or "",
            "roles": self.roles or [],
            "is_subscribed": self.is_subscribed,
            "error_message": self.error_message or "",
        }


class UserInfo(BaseModel):
    name: str = ""
    surname: str = ""
    patronymic: str = ""
    email: str
