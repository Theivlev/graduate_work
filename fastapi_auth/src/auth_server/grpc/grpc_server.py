from uuid import UUID


import grpc
import src.auth_server.grpc.auth_pb2 as auth_pb2
import src.auth_server.grpc.auth_pb2_grpc as auth_pb2_grpc
from src.auth_server.abc.base import BaseAuthService
from src.auth_server.schemas.models import UserInfo
from src.services.user_service import get_user_service
from src.db.postgres import AsyncSessionLocal
from src.services.user_service import UserService

class GRPCAuthService(auth_pb2_grpc.AuthServiceServicer, BaseAuthService):
    def CheckToken(self, request, context):
        token = request.token
        result = self.check_token(token)
        return auth_pb2.CheckTokenResponse(**result.to_proto())

    async def GetUserInfo(self, request, context):
        async with AsyncSessionLocal() as session:
            user_service = UserService(session)
            user_model = await user_service.get_model(UUID(request.user_id))
            user = UserInfo.model_validate(user_model, from_attributes=True)
            return auth_pb2.GetUserInfoResponse(**user.model_dump())    

    async def serve(self):
        server = grpc.aio.server()
        auth_pb2_grpc.add_AuthServiceServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{self.port}")
        await server.start()
        await server.wait_for_termination()

    async def stop(self):
        if hasattr(self, "server"):
            await self.server.stop(5)
