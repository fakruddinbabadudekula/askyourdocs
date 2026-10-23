from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class TokenStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class RefreshToken:
    token_id: UUID
    hashed_token: str
    status: TokenStatus
    user_id: UUID
    created_at: datetime
    family_id: UUID
    expires_at: datetime
    revoked_at: datetime | None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RefreshToken):
            return NotImplemented
        return self.token_id == other.token_id

    def __hash__(self) -> int:
        return hash(self.token_id)

    @classmethod
    def create(
        cls,
        hashed_token: str,
        user_id: UUID,
        family_id: UUID,
        created_at: datetime,
        expires_at: datetime,
    ) -> RefreshToken:
        return cls(
            token_id=uuid4(),
            hashed_token=hashed_token,
            status=TokenStatus.ACTIVE,
            user_id=user_id,
            created_at=created_at,
            family_id=family_id,
            expires_at=expires_at,
            revoked_at=None,
        )
