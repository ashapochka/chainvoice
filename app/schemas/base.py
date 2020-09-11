from pydantic import BaseModel
from fastapi_utils.api_model import APIModel


class UID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return cls(v)


class BaseSchema(APIModel):
    class Config:
        orm_mode = False


class UIDSchema(BaseSchema):
    uid: UID
