from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Identity, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity

if TYPE_CHECKING:
    from app.models.user import User


class Role(BaseEntity):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    parent_role_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("roles.id"), nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Self-referential relationships
    parent: Mapped["Role | None"] = relationship(
        "Role",
        remote_side="Role.id",
        back_populates="children",
        lazy="noload",
    )
    children: Mapped[list["Role"]] = relationship(
        "Role",
        back_populates="parent",
        lazy="noload",
    )
    # Users in this role
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
        foreign_keys="[User.role_id]",
        lazy="noload",
        primaryjoin="and_(User.role_id == Role.id, User.is_deleted == False)",
        viewonly=True,
    )
