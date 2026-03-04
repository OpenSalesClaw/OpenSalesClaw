"""SQLAlchemy models for CustomObject and CustomObjectRecord."""

from typing import Any

from sqlalchemy import BigInteger, Boolean, ForeignKey, Identity, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class CustomObject(BaseEntity):
    """Metadata definition for a user-created custom object (like a custom Salesforce object)."""

    __tablename__ = "custom_objects"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    # Unique snake_case identifier used in API URLs, e.g. "project", "warranty_claim"
    api_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    plural_label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Lucide icon name, e.g. "box", "folder", "star"
    icon_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    records: Mapped[list["CustomObjectRecord"]] = relationship(
        "CustomObjectRecord",
        back_populates="custom_object",
        lazy="noload",
    )


class CustomObjectRecord(BaseEntity):
    """A single record belonging to a CustomObject — fields stored as JSONB."""

    __tablename__ = "custom_object_records"
    __table_args__ = (Index("idx_custom_object_records_data", "data", postgresql_using="gin"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    custom_object_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("custom_objects.id"), nullable=False, index=True
    )
    # Human-readable record name (like Salesforce's "Name" field)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    # The dynamic fields defined via CustomFieldDefinitions for this object
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    custom_object: Mapped["CustomObject"] = relationship("CustomObject", back_populates="records")
