import jwt
from src.core.config import project_settings


def encode_jwt(data):
    return jwt.encode(data, project_settings.secret, algorithm="HS256", audience="fastapi-users:auth")


def decode_jwt(token):
    return jwt.decode(token, project_settings.secret, algorithms="HS256", audience="fastapi-users:auth")
