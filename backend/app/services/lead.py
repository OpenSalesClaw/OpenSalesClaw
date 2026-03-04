from typing import Any

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.base import CRUDService


class LeadService(CRUDService[Lead, LeadCreate, LeadUpdate]):
    model = Lead

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if status := filters.get("status"):
            query = query.where(Lead.status == status)
        if company := filters.get("company"):
            query = query.where(Lead.company.ilike(f"%{company}%"))
        if email := filters.get("email"):
            query = query.where(Lead.email.ilike(f"%{email}%"))
        return query


lead_service = LeadService()

# Convenience aliases
get_lead_by_id = lead_service.get_by_id
list_leads = lead_service.list
create_lead = lead_service.create
update_lead = lead_service.update
delete_lead = lead_service.delete
