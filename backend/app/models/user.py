from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Identity, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity

if TYPE_CHECKING:
    from app.models.role import Role


class User(BaseEntity):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    role_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("roles.id"), nullable=True, index=True)

    role: Mapped["Role | None"] = relationship("Role", foreign_keys=[role_id], back_populates="users", lazy="noload")
