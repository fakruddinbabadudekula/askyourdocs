from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4, UUID
from enum import Enum
from typing import Any


@dataclass
class Citation:
    index: int
    id: UUID

    @classmethod
    def create(cls, index: int, id: UUID):
        return cls(index=index, id=id)

    def as_dict(self) -> dict[str, Any]:
        return {"index": self.index, "id": self.id}


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    message_id: UUID
    role: MessageRole
    content: str
    notebook_id: UUID
    citation_refs: list[Citation] | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        role: MessageRole,
        content: str,
        notebook_id: UUID,
        citation_refs: list[Citation] | None = None,
    ) -> "Message":
        return cls(
            message_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            role=role,
            citation_refs=citation_refs,
            content=content,
            notebook_id=notebook_id,
        )
