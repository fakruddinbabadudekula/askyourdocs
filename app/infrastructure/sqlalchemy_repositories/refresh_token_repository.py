from datetime import datetime
from app.application.ports.repositories.refresh_token_repository import (
    AbstractRefreshTokenRepository,
)
from app.domain.refresh_token import RefreshToken, TokenStatus
from app.infrastructure.sqlalchemy_repositories.models.refresh_token import (
    RefreshToken as OrmRefreshToken,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from app.infrastructure.sqlalchemy_repositories.mappers import (
    refresh_token_to_orm,
    orm_to_refresh_token,
)
from uuid import UUID


class RefreshTokenRepository(AbstractRefreshTokenRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, token: RefreshToken) -> None:
        new_token_orm = refresh_token_to_orm(token)
        self._db.add(new_token_orm)

    async def get_token_by_id(self, token_id: UUID) -> RefreshToken | None:
        result = await self._db.execute(
            select(OrmRefreshToken).where(OrmRefreshToken.token_id == token_id)
        )
        token_orm = result.scalar_one_or_none()
        return orm_to_refresh_token(token_orm) if token_orm else None

    async def get_token_by_hash(self, hash_token: str) -> RefreshToken | None:
        result = await self._db.execute(
            select(OrmRefreshToken).where(OrmRefreshToken.hashed_token == hash_token)
        )
        token_orm = result.scalar_one_or_none()
        return orm_to_refresh_token(token_orm) if token_orm else None

    async def revoke_all_tokens_by_family_id(
        self, family_id: UUID, now: datetime
    ) -> None:
        await self._db.execute(
            update(OrmRefreshToken)
            .where(OrmRefreshToken.family_id == family_id)
            .values(status=TokenStatus.REVOKED, revoked_at=now)
        )

    async def update(self, token: RefreshToken) -> None:
        await self._db.execute(
            update(OrmRefreshToken)
            .where(OrmRefreshToken.token_id == token.token_id)
            .values(status=token.status, revoked_at=token.revoked_at)
        )

    async def delete(self, token_id: UUID) -> None:
        await self._db.execute(
            delete(OrmRefreshToken).where(OrmRefreshToken.token_id == token_id)
        )
