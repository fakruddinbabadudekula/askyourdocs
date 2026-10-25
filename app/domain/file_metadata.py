from dataclasses import dataclass
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime, timezone


class FileType(str, Enum):
    PDF = "pdf"


@dataclass
class FileMetadata:
    file_id: UUID
    notebook_id: UUID
    type: FileType
    name: str
    size: int
    created_at: datetime

    @classmethod
    def create(
        cls, notebook_id: UUID, type: FileType, name: str, size: int
    ) -> "FileMetadata":
        return cls(
            file_id=uuid4(),
            notebook_id=notebook_id,
            type=type,
            name=name,
            size=size,
            created_at=datetime.now(timezone.utc),
        )
