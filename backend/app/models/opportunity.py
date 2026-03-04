from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, ForeignKey, Identity, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.contact import Contact

OPPORTUNITY_STAGES: list[str] = [
    "Prospecting",
    "Qualification",
    "Needs Analysis",
    "Value Proposition",
    "Id. Decision Makers",
    "Perception Analysis",
    "Proposal/Price Quote",
    "Negotiation/Review",
    "Closed Won",
    "Closed Lost",
]

DEFAULT_STAGE_PROBABILITIES: dict[str, int] = {
    "Prospecting": 10,
    "Qualification": 20,
    "Needs Analysis": 20,
    "Value Proposition": 50,
    "Id. Decision Makers": 60,
    "Perception Analysis": 70,
    "Proposal/Price Quote": 75,
    "Negotiation/Review": 90,
    "Closed Won": 100,
    "Closed Lost": 0,
}


class Opportunity(BaseEntity):
    __tablename__ = "opportunities"
    __table_args__ = (CheckConstraint("probability >= 0 AND probability <= 100", name="probability"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("accounts.id"), nullable=True, index=True)
    contact_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("contacts.id"), nullable=True)
    stage: Mapped[str] = mapped_column(String(100), nullable=False, server_default="Prospecting", index=True)
    probability: Mapped[int | None] = mapped_column(Integer, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    close_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lead_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    next_step: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_won: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
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
