from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginationParams
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from app.services.base import CRUDService, escape_like


class ContactService(CRUDService[Contact, ContactCreate, ContactUpdate]):
    model = Contact

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if account_id := filters.get("account_id"):
            query = query.where(Contact.account_id == account_id)
        if last_name := filters.get("last_name"):
            query = query.where(Contact.last_name.ilike(f"%{escape_like(last_name)}%", escape="\\"))
        if email := filters.get("email"):
            query = query.where(Contact.email.ilike(f"%{escape_like(email)}%", escape="\\"))
        return query

    async def list(
        self,
        db: AsyncSession,
        pagination: PaginationParams,
        *,
        order_by: Any | None = None,
        **filters: Any,
    ) -> tuple[list[Contact], int]:
        """Contacts default to alphabetical by last name."""
        if order_by is None:
            order_by = Contact.last_name.asc()
        return await super().list(db, pagination, order_by=order_by, **filters)


contact_service = ContactService()
