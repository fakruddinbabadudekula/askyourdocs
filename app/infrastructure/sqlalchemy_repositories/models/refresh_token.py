from app.infrastructure.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import DateTime, func, Text, ForeignKey
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.schemas.refresh_token import TokenStatus


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    token_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
        primary_key=True,
    )
    hashed_token: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("user.user_id"), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    family_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[TokenStatus] = mapped_column(default=TokenStatus.ACTIVE)
    revoked_at: Mapped[uuid.UUID] = mapped_column(DateTime(timezone=True), nullable=True)