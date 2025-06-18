import logging

import grpc
import src.auth_server.grpc.auth_pb2 as auth_pb2
import src.auth_server.grpc.auth_pb2_grpc as auth_pb2_grpc
from src.auth_server.abc.abstract_auth_client import AbstractAuthClient
from src.auth_server.schemas.models import TokenPayload, TokenValidationResult
from src.core.config import project_settings


class GRPCAuthClient(AbstractAuthClient):
    def __init__(self, host: str = project_settings.auth_grpc_host, port: int = project_settings.auth_grpc_port):
        self.target = f"{host}:{port}"

    async def check_token(self, token: TokenPayload) -> TokenValidationResult:
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = auth_pb2_grpc.AuthServiceStub(channel)
            request = auth_pb2.CheckTokenRequest(token=token.token)
            try:
                response = await stub.CheckToken(request)
                return TokenValidationResult(
                    is_valid=response.is_valid,
                    user_id=response.user_id,
                    is_subscribed=response.is_subscribed,
                    error_message=response.error_message,
                )
            except grpc.RpcError as e:
                logging.error(f"gRPC call error: {e}")
                return TokenValidationResult(
                    is_valid=False,
                    user_id=None,
                    is_subscribed=False,
                    error_message=str(e),
                )
