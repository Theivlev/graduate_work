from abc import ABC, abstractmethod

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from src.auth_server.schemas.models import CheckTokenResult
from src.core.config import auth_settings


class AbstractAuthServer(ABC):
    def __init__(self, port):
        self.port = port

    @abstractmethod
    async def serve(self):
        pass


class AbstractJWTService(ABC):
    @staticmethod
    def check_token(token: str) -> CheckTokenResult:
        if not token:
            return CheckTokenResult(
                is_valid=False,
                user_id=None,
                error_message="No token provided",
            )

        try:
            payload = jwt.decode(
                token,
                auth_settings.secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            return CheckTokenResult(
                is_valid=True,
                user_id=payload.get("sub"),
                is_subscribed=True,
                error_message=None,
            )

        except ExpiredSignatureError:
            return CheckTokenResult(
                is_valid=False,
                user_id=None,
                is_subscribed=False,
                error_message="Token expired",
            )
        except InvalidTokenError as e:
            return CheckTokenResult(
                is_valid=False,
                user_id=None,
                is_subscribed=False,
                error_message=f"Invalid token: {str(e)}",
            )


class BaseAuthService(AbstractJWTService, AbstractAuthServer):
    """
    Basic class: knows how to check the token and run the server.
    Specific implementations can add GRPC/HTTP handlers.
    """

    pass
