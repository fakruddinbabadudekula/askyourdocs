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

    def is_revoked(self) -> bool:
        return self.status == TokenStatus.REVOKED

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at < now

    def mark_expired(self, now: datetime) -> None:
        if self.expires_at <= now and self.status == TokenStatus.ACTIVE:
            self.status = TokenStatus.EXPIRED

    def revoke(self, now: datetime) -> None:
        if self.status == TokenStatus.ACTIVE:
            self.status = TokenStatus.REVOKED
            self.revoked_at = now

    def is_valid(self, now: datetime) -> bool:
        return self.status == TokenStatus.ACTIVE and not self.is_expired(now)
