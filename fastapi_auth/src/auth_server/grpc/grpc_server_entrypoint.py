import asyncio
from src.auth_server.grpc.grpc_server import GRPCAuthService
from src.core.config import project_settings

async def main():
    port = project_settings.auth_grpc_port
    grpc_auth_service = GRPCAuthService(port=port)
    await grpc_auth_service.serve()

if __name__ == "__main__":
    asyncio.run(main())