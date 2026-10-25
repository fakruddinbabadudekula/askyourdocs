from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.message import Message
from enum import Enum


class MessageSort(str, Enum):
    CREATED_AT_ASC = "created_at_asc"
    CREATED_AT_DESC = "created_at_desc"


class AbstractMessageRepository(ABC):

    @abstractmethod
    async def save(self, message: Message) -> None: ...

    @abstractmethod
    async def get_message(self, message_id: UUID) -> Message | None: ...

    @abstractmethod
    async def get_messages(
        self, notebook_id: UUID, order_by: MessageSort = MessageSort.CREATED_AT_ASC
    ) -> list[Message | None]: ...

    @abstractmethod
    async def delete_message(self, message_id: UUID) -> None: ...
