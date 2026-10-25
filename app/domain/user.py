from __future__ import annotations
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class User:
    name: str
    email: str
    hashed_password: str
    user_id: uuid.UUID
    created_at: datetime

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        return hash(self.user_id)

    @classmethod
    def create(cls, name: str, hashed_password: str, email: str) -> User:
        """Create a new user with a fresh identity."""
        return cls(
            name=name,
            hashed_password=hashed_password,
            email=email,
            user_id=uuid.uuid4(),
            created_at=datetime.now(timezone.utc),
        )
