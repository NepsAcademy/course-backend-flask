from pydantic.v1 import BaseModel


class DefaultResponse(BaseModel):
    msg: str
