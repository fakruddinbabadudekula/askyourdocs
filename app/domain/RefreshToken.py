from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime, timezone
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

    def revoke(self) -> None:
        if self.status != TokenStatus.ACTIVE:
            raise ValueError("Cannot revoke an already revoked/expired token")
        self.status = TokenStatus.REVOKED
        self.revoked_at = datetime.now(timezone.utc)

    def is_revoked(self) -> bool:
        return self.status == TokenStatus.REVOKED

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        return self.status == TokenStatus.ACTIVE and not self.is_expired
