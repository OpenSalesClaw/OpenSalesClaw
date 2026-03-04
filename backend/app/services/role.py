"""Business logic for the Role entity."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from app.services.base import CRUDService


class RoleService(CRUDService[Role, RoleCreate, RoleUpdate]):
    model = Role

    def apply_list_filters(self, query: Any, **filters: Any) -> Any:
        if name := filters.get("name"):
            query = query.where(Role.name.ilike(f"%{name}%"))
        return query

    async def create(self, db: AsyncSession, data: RoleCreate, created_by_id: int | None = None) -> Role:
        # Validate parent exists and detect cycles (no cycle possible on create since this role doesn't exist yet)
        if data.parent_role_id is not None:
            await self.get_by_id(db, data.parent_role_id)
        return await super().create(db, data, created_by_id=created_by_id)

    async def update(
        self, db: AsyncSession, record_id: int, data: RoleUpdate, updated_by_id: int | None = None
    ) -> Role:
        if data.parent_role_id is not None:
            if data.parent_role_id == record_id:
                raise ConflictError("A role cannot be its own parent.")
            await self._check_no_cycle(db, record_id, data.parent_role_id)
        return await super().update(db, record_id, data, updated_by_id=updated_by_id)

    async def _check_no_cycle(self, db: AsyncSession, role_id: int, new_parent_id: int) -> None:
        """Walk the ancestor chain of new_parent_id; if role_id appears, it's a cycle."""
        visited: set[int] = set()
        current_id: int | None = new_parent_id
        while current_id is not None:
            if current_id in visited:
                break  # already visited, malformed graph but no cycle involving role_id
            if current_id == role_id:
                raise ConflictError("Setting this parent would create a circular role hierarchy.")
            visited.add(current_id)
            parent_role = await self.get_by_id(db, current_id)
            current_id = parent_role.parent_role_id

    async def get_hierarchy(self, db: AsyncSession) -> list[dict[str, Any]]:
        """Return all roles as a flat list with parent info for tree construction."""
        items, _ = await self.list(db, type("P", (), {"offset": 0, "limit": 1000})())
        return [
            {
                "id": role.id,
                "name": role.name,
                "parent_role_id": role.parent_role_id,
                "description": role.description,
            }
            for role in items
        ]


role_service = RoleService()

get_role_by_id = role_service.get_by_id
list_roles = role_service.list
create_role = role_service.create
update_role = role_service.update
delete_role = role_service.delete
get_role_hierarchy = role_service.get_hierarchy
