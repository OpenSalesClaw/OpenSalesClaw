# Re-export all ORM models so that `Base.metadata` includes every table.
# Import this module (or app.models) in alembic/env.py for autogenerate.
from app.models.account import Account  # noqa: F401
from app.models.base import Base  # noqa: F401
from app.models.case import Case  # noqa: F401
from app.models.contact import Contact  # noqa: F401
from app.models.custom_field_definition import CustomFieldDefinition  # noqa: F401
from app.models.custom_object import CustomObject, CustomObjectRecord  # noqa: F401
from app.models.lead import Lead  # noqa: F401
from app.models.opportunity import Opportunity  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.user import User  # noqa: F401
