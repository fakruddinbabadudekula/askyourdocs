"""Module for schemas which are specific for auth router"""

from pydantic import BaseModel, ConfigDict, field_validator,EmailStr
from datetime import datetime
class BaseUser(BaseModel):
    email: str
    name: str
    # what model_config means, how we create the instance of this class like this right BaseUser(key_value), this allows BaseUser(dict/another_dataclass_instance)
    model_config = ConfigDict(from_attributes=True)


class RegisterUser(BaseModel):
    name: str
    password: str
    email: EmailStr

    @field_validator("password")
    @classmethod
    def password_validator(cls, value: str) -> str:
        if len(value) < 7:
            raise ValueError("Password must be at least 8 characters")
        return value


class AccessTokenResponse(BaseModel):
    token: str
    expire_at: int
    token_type: str = "bearer"

    @field_validator("expire_at", mode="before")
    @classmethod
    def convert_datetime_to_timestamp(cls, value):
        if not isinstance(value, datetime):
            raise ValueError(
                "expire_at accept only datetime instance and return into int"
            )

        return int(
            value.timestamp() * 1000
        )  # it returns into milliseconds, bcz most of frontend uses js/ts so that it can be easy to work will ms.


class DeleteUser(BaseModel):
    email: str
    password: str


class LoginUser(BaseModel):
    email: str
    password: str
