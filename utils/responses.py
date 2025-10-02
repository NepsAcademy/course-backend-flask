from pydantic import BaseModel


class DefaultResponse(BaseModel):
    msg: str
