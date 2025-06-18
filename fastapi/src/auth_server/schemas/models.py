from pydantic import BaseModel


class TokenValidationResult(BaseModel):
    is_valid: bool
    user_id: str | None
    is_subscribed: bool
    error_message: str | None


class TokenPayload(BaseModel):
    token: str
