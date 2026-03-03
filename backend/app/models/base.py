from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class StandardColumns:
    """Mixin that adds all standard audit/metadata columns required by every entity table."""

    sfid: Mapped[str | None] = mapped_column(Text, nullable=True)

    custom_fields: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    owner_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", use_alter=True), nullable=True
    )
    created_by_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", use_alter=True), nullable=True
    )
    updated_by_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", use_alter=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    deleted_by_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", use_alter=True), nullable=True
    )
