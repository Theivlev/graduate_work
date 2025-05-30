from pydantic import BaseModel


class EmailMessage(BaseModel):
    user_id: str
    subject: str
    template: str
    confirmation_link: str
