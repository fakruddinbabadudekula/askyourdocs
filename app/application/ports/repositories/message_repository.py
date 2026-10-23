from abc import ABC, abstractmethod
from uuid import UUID
from app.schemas.message import Message


class AbstractMessageRepository(ABC):

    @abstractmethod
    async def save(self, message: Message) -> None: ...

    @abstractmethod
    async def update(self, message: Message) -> None: ...

    @abstractmethod
    async def get_message(self, message_id: UUID) -> Message | None: ...

    @abstractmethod
    async def get_messages(self, notebook_id: UUID) -> list[Message | None]: ...

    @abstractmethod
    async def delete_message(self, message_id: UUID) -> None: ...
