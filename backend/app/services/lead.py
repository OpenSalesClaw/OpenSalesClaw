from typing import Any

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.base import CRUDService, escape_like


class LeadService(CRUDService[Lead, LeadCreate, LeadUpdate]):
    model = Lead

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if status := filters.get("status"):
            query = query.where(Lead.status == status)
        if company := filters.get("company"):
            query = query.where(Lead.company.ilike(f"%{escape_like(company)}%", escape="\\"))
        if email := filters.get("email"):
            query = query.where(Lead.email.ilike(f"%{escape_like(email)}%", escape="\\"))
        return query


lead_service = LeadService()
