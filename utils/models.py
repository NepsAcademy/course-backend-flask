from pydantic import BaseModel, ConfigDict


class OrmBase(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

    def to_response_dict(self):
        return self.model_dump(mode="json")
