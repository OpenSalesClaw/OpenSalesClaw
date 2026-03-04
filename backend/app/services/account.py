from typing import Any

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from app.services.base import CRUDService


class AccountService(CRUDService[Account, AccountCreate, AccountUpdate]):
    model = Account

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if name := filters.get("name"):
            query = query.where(Account.name.ilike(f"%{name}%"))
        if type_ := filters.get("type"):
            query = query.where(Account.type == type_)
        if industry := filters.get("industry"):
            query = query.where(Account.industry.ilike(f"%{industry}%"))
        return query


account_service = AccountService()

# Convenience aliases for backward-compatible function-style access
get_account_by_id = account_service.get_by_id
list_accounts = account_service.list
create_account = account_service.create
update_account = account_service.update
delete_account = account_service.delete
