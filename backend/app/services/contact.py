from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import PaginationParams

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate
from app.services.base import CRUDService


class ContactService(CRUDService[Contact, ContactCreate, ContactUpdate]):
    model = Contact

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if account_id := filters.get("account_id"):
            query = query.where(Contact.account_id == account_id)
        if last_name := filters.get("last_name"):
            query = query.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email := filters.get("email"):
            query = query.where(Contact.email.ilike(f"%{email}%"))
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

# Convenience aliases
get_contact_by_id = contact_service.get_by_id
list_contacts = contact_service.list
create_contact = contact_service.create
update_contact = contact_service.update
delete_contact = contact_service.delete
