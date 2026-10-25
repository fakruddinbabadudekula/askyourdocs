from app.schemas.message import Message
from app.application.ports.repositories.message_repository import (
    AbstractMessageRepository,
)
from app.infrastructure.sqlalchemy_repositories.models.message import (
    Message as OrmMessage,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.infrastructure.sqlalchemy_repositories.mappers import (
    message_to_orm,
    orm_to_message,
)
from uuid import UUID


class MessageRepository(AbstractMessageRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, message: Message) -> None:
        self._db.add(message_to_orm(message))

    async def get_message(self, message_id: UUID) -> Message | None:
        result = await self._db.execute(
            select(OrmMessage).where(OrmMessage.message_id == message_id)
        )
        message_orm = result.scalar_one_or_none()
        return orm_to_message(message_orm) if message_orm else None

    async def get_messages(self, notebook_id: UUID) -> list[Message | None]:
        result = await self._db.execute(
            select(OrmMessage).where(OrmMessage.notebook_id == notebook_id)
        )
        messages_orm = result.scalars().all()
        return [orm_to_message(message) for message in messages_orm]

    async def delete_message(self, message_id: UUID) -> None:
        await self._db.execute(
            delete(OrmMessage).where(OrmMessage.message_id == message_id)
        )
