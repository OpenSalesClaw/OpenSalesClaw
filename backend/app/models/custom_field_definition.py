from typing import Any

from sqlalchemy import BigInteger, Boolean, Identity, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class CustomFieldDefinition(BaseEntity):
    __tablename__ = "custom_field_definitions"
    __table_args__ = (UniqueConstraint("object_name", "field_name", name="uq_custom_field_definitions_object_field"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    # e.g. 'accounts', 'contacts'
    object_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Text, Number, Date, DateTime, Boolean, Picklist, MultiPicklist, Email, URL, TextArea, Currency
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    picklist_values: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    field_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
