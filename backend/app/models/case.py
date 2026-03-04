from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Identity, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.contact import Contact

CASE_STATUSES: list[str] = ["New", "Working", "Escalated", "Closed"]
CASE_PRIORITIES: list[str] = ["Low", "Medium", "High", "Critical"]


class Case(BaseEntity):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    case_number: Mapped[str | None] = mapped_column(String(30), nullable=True, unique=True)
    account_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("accounts.id"), nullable=True, index=True
    )
    contact_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("contacts.id"), nullable=True, index=True
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False, server_default="New", index=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, server_default="Medium", index=True)
    origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    account: Mapped["Account | None"] = relationship(
        "Account",
        foreign_keys=[account_id],
        lazy="noload",
    )
    contact: Mapped["Contact | None"] = relationship(
        "Contact",
        foreign_keys=[contact_id],
        lazy="noload",
    )
