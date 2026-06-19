"""
Organization membership table model.

Canonical definition for ``love_engine_organizationmembership``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import ConfigDict, model_validator

from love_engine.models.budget import LOVE_ENGINE_BudgetTable
from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_OrganizationMembershipTable(LoveEnginePydanticObjectBase):
    """Tracks which organizations a user belongs to and their spend within it."""

    user_id: str
    organization_id: str
    user_role: Optional[str] = None
    spend: float = 0.0
    budget_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user: Optional[Any] = None
    love_engine_budget_table: Optional[LOVE_ENGINE_BudgetTable] = None
    user_email: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=())

    @model_validator(mode="after")
    def populate_user_email(self) -> "LOVE_ENGINE_OrganizationMembershipTable":
        if self.user_email is None and self.user is not None:
            if isinstance(self.user, dict):
                self.user_email = self.user.get("user_email")
            else:
                self.user_email = getattr(self.user, "user_email", None)
        return self
