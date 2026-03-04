from typing import Any

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.base import CRUDService, escape_like


class AccountService(CRUDService[Account, AccountCreate, AccountUpdate]):
    model = Account

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if name := filters.get("name"):
            query = query.where(Account.name.ilike(f"%{escape_like(name)}%", escape="\\"))
        if type_ := filters.get("type"):
            query = query.where(Account.type == type_)
        if industry := filters.get("industry"):
            query = query.where(Account.industry.ilike(f"%{escape_like(industry)}%", escape="\\"))
        return query


account_service = AccountService()
