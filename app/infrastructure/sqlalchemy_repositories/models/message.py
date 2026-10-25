"""Module for message database model"""

from typing import Any
from app.infrastructure.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime, func, Text, Enum as SqlEnum
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSON
from app.schemas.message import MessageRole
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.sqlalchemy_repositories.models.notebook import Notebook


class Message(Base):
    __tablename__ = "message"
    message_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
        primary_key=True,
    )
    notebook_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("notebook.notebook_id"))
    content: Mapped[str] = mapped_column(Text)
    role: Mapped[MessageRole] = mapped_column(SqlEnum(MessageRole), nullable=False)

    citation_refs: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    notebook: Mapped["Notebook"] = relationship(back_populates="messages")
