"""
Organization table model.

Canonical definition for ``love_engine_organizationtable``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from typing import List, Optional

from love_engine.models.budget import LOVE_ENGINE_BudgetTable
from love_engine.models.object_permission import LOVE_ENGINE_ObjectPermissionTable
from love_engine.models.user import LOVE_ENGINE_UserTable
from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_OrganizationTable(LoveEnginePydanticObjectBase):
    """Represents user-controllable params for a LOVE_ENGINE_OrganizationTable record"""

    organization_id: Optional[str] = None
    organization_alias: Optional[str] = None
    budget_id: str
    spend: float = 0.0
    metadata: Optional[dict] = None
    models: List[str] = []
    model_spend: Optional[dict] = {}
    created_by: str
    updated_by: str
    users: Optional[List[LOVE_ENGINE_UserTable]] = None
    love_engine_budget_table: Optional[LOVE_ENGINE_BudgetTable] = None
    object_permission: Optional[LOVE_ENGINE_ObjectPermissionTable] = None
    object_permission_id: Optional[str] = None
