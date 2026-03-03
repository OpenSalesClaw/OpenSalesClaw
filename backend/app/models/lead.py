from datetime import datetime

from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, StandardColumns


class Lead(StandardColumns, Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Picklist: New, Contacted, Qualified, Unqualified, Converted
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="New", server_default="New", index=True)
    lead_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)

    converted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    converted_account_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    converted_contact_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
