from pydantic.v1 import BaseModel


class OrmBase(BaseModel):
    id: int

    class Config:
        orm_mode = True
