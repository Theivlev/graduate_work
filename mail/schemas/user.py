from pydantic import BaseModel


class GetUserInfoResponse(BaseModel):
    name: str = ""
    surname: str = ""
    patronymic: str = ""
    email: str
