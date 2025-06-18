from abc import ABC, abstractmethod

from src.auth_server.schemas.models import TokenPayload, TokenValidationResult


class AbstractAuthClient(ABC):
    """
    Abstract authorization client: defines how we will
    check the token and where to redirect when the user is not authorized.
    """

    @abstractmethod
    async def check_token(self, token: TokenPayload) -> TokenValidationResult:
        """
        Check the token and return a dictionary of the following form:
        """
        pass
