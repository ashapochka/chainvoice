from pydantic import BaseModel


class UID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return cls(v)


class BaseSchema(BaseModel):
    pass


class UIDSchema(BaseSchema):
    uid: UID
