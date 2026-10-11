from abc import ABC, abstractmethod
from datetime import datetime
from typing import Literal


class PasswordHasher(ABC):
    @abstractmethod
    def hash_password(self, plain_password: str) -> str: ...
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...


class TokenService(ABC):
    access_token_expiry_time_minutes: int
    refresh_toekn_exprity_time_days: int
    secret_key: str
    algorithm: str

    @abstractmethod
    def create_token(
        self, subject: str, now: datetime, type: Literal["access", "refresh"]
    ) -> tuple[str, datetime]: ...
    @abstractmethod
    def decode_token(self, token: str) -> dict: ...


class HashService(ABC):
    @abstractmethod
    def hash_content(self, raw: str) -> str: ...
