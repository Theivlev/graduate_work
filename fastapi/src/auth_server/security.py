from functools import lru_cache
from typing import Optional

from fastapi.params import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.auth_server.abc.abstract_auth_client import AbstractAuthClient
from src.auth_server.grpc.grpc_client import GRPCAuthClient
from src.auth_server.schemas.models import TokenPayload, TokenValidationResult

from fastapi import Depends, HTTPException, status

security_scheme = HTTPBearer(auto_error=False)


@lru_cache
def get_auth_client() -> AbstractAuthClient:
    """
    Factory that returns an implementation of the authorization client.
    Currently, this is GRPCAuthClient.
    """
    return GRPCAuthClient()


async def require_valid_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    auth_client: AbstractAuthClient = Depends(get_auth_client),
) -> TokenValidationResult:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth scheme",
        )

    token = credentials.credentials
    validation_result = await auth_client.check_token(TokenPayload(token=token))

    if not validation_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token invalid: {validation_result.error_message}"
        )

    return validation_result
