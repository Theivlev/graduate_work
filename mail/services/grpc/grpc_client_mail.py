from functools import lru_cache

import grpc
from google.protobuf.json_format import MessageToDict

from core.config import grpc_settings
from schemas.user import GetUserInfoResponse
from services.grpc import auth_pb2, auth_pb2_grpc


class GRPCAuthClient:
    def __init__(self, host: str = "grpc_auth",
                 port: int = grpc_settings.auth_grpc_port):
        self.target = f"{host}:{port}"
        print(self.target, "target from MAIL")

    async def get_user_info(self, user_id: str) -> GetUserInfoResponse:
      async with grpc.aio.insecure_channel(self.target) as channel:
          stub = auth_pb2_grpc.AuthServiceStub(channel)
          request = auth_pb2.GetUserInfoRequest(user_id=user_id)
          try:
            response = await stub.GetUserInfo(request)
            print(response, "response from MAIL", flush=True)
            user_dict = MessageToDict(response)
            print(user_dict, "user_dict from MAIL", flush=True)
            user = GetUserInfoResponse.model_validate(user_dict)
            print(user, "user from MAIL", flush=True)
            return user
          except Exception as e:
            print(e, "error from MAIL")
            raise e


@lru_cache
def get_auth_client() -> GRPCAuthClient:
    print("get_auth_client")
    return GRPCAuthClient()