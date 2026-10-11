from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey
from app.infrastructure.db import Base
import uuid


class Chunk(Base):
    __tablename__ = "chunk"
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
        primary_key=True,
    )

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("files_metadata.file_id"))
