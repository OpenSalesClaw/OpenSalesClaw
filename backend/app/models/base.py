from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Identity, MetaData, String
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Naming convention ensures SQLAlchemy can emit DROP CONSTRAINT by name for
# use_alter FK constraints and any other named constraints.
_NAMING_CONVENTION: dict[str, str] = {
    "ix": "idx_%(table_name)s_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=_NAMING_CONVENTION)


class StandardColumns:
    """Mixin that adds all standard audit/metadata columns required by every entity table."""

    sfid: Mapped[str | None] = mapped_column(String(40), nullable=True)

    custom_fields: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    owner_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", use_alter=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", use_alter=True), nullable=True)
    updated_by_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", use_alter=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    deleted_by_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", use_alter=True), nullable=True)
