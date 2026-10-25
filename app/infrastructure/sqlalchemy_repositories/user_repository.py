from app.application.ports.repositories.user_repository import AbstractUserRepository
from app.core.exceptions import DuplicateResourceException
from app.domain.user import User
from app.infrastructure.sqlalchemy_repositories.models.user import User as OrmUser
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.infrastructure.sqlalchemy_repositories.mappers import orm_to_user, user_to_orm
from uuid import UUID


class UserRepository(AbstractUserRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_user_by_email(self, user_email: str) -> User | None:
        result = await self._db.execute(
            select(OrmUser).where(OrmUser.email == user_email)
        )
        user_orm = result.scalars().first()
        return orm_to_user(user_orm) if user_orm else None

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        result = await self._db.execute(
            select(OrmUser).where(OrmUser.user_id == user_id)
        )
        user_orm = result.scalars().first()
        return orm_to_user(user_orm) if user_orm else None

    async def save(self, user: User) -> None:
        new_user_orm = user_to_orm(user)
        try:
            self._db.add(new_user_orm)
            await self._db.flush()
        except IntegrityError as e:
            await self._db.rollback()  # Whoever corrupts the session state is responsible for cleaning it up.Without trusting what caller do next.
            # Then why doesn uow__exist__() rollback, if we clean, we manually do rollback like above exceptions where it raised from user things right, but uow rollback is used to rollback for unkown errors like timeout,connection related.
            raise DuplicateResourceException(
                "user_already_exist", details={"user_email": new_user_orm.email}
            )

    async def delete_user(self, user_id: UUID) -> None:
        await self._db.execute(delete(OrmUser).where(OrmUser.user_id == user_id))
