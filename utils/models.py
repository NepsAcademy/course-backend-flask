from pydantic import BaseModel, ConfigDict


class OrmBase(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)
