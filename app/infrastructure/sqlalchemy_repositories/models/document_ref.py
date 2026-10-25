from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey
from app.infrastructure.db import Base
import uuid


class DocumentRef(Base):
    __tablename__ = "document_ref"
    doc_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
        primary_key=True,
    )

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_metadata.file_id"))