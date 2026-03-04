from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Identity, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, StandardColumns

if TYPE_CHECKING:
    from app.models.contact import Contact


class Account(StandardColumns, Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # Picklist: Customer, Partner, Prospect, Vendor, Other
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    billing_street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    billing_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    billing_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    billing_postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    billing_country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    annual_revenue: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    number_of_employees: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    contacts: Mapped[list["Contact"]] = relationship(  # noqa: F821
        "Contact",
        back_populates="account",
        primaryjoin="and_(Contact.account_id == Account.id, Contact.is_deleted == false())",
        lazy="noload",
        viewonly=True,
    )
