from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class TokenData:
    access_token: str
    refresh_token: str
    access_expire_time: datetime
    refresh_expire_time: datetime


@dataclass
class LoginData:
    email: str
    password: str


@dataclass
class RefreshSchema:
    user_id: uuid.UUID
    hashed_token: str
    family_id: uuid.UUID
    expires_at: datetime


@dataclass
class RegisterUser:
    name: str
    password: str
    email: str
