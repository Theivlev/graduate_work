from typing import List

from fastapi import HTTPException, Request, status
from fastapi_auth.src.utils.tokenuser import decode_jwt


class UnusualException(HTTPException):
    def __init__(self, status_code: int, message: str, code: str, target: str):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.target = target


def role_verification(allowed_roles: List[str]):
    def verify_roles(request: Request = Request):
        access_token: dict = decode_jwt(request.cookies.get("access"))
        if access_token.get("role") not in allowed_roles:
            raise UnusualException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Ошибка доступа",
                code="Access denied",
                target="role",
            )

    return verify_roles
