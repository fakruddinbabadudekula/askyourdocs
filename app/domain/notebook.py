from uuid import UUID, uuid4
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Notebook:
    notebook_id: UUID
    title: str | None
    user_id: UUID
    created_at: datetime

    @classmethod
    def create(cls, user_id: UUID, title: str | None = None) -> "Notebook":
        return cls(
            notebook_id=uuid4(),
            user_id=user_id,
            title=title,
            created_at=datetime.now(timezone.utc),
        )

    def rename_title(self, title: str) -> None:
        self.title = title
