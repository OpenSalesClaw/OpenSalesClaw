from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, StandardColumns


class Contact(StandardColumns, Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    account_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("accounts.id"), nullable=True, index=True
    )
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    mobile_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)

    mailing_street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mailing_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mailing_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mailing_postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    mailing_country: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    account: Mapped["Account | None"] = relationship(  # noqa: F821
        "Account",
        back_populates="contacts",
        foreign_keys=[account_id],
        lazy="noload",
    )
