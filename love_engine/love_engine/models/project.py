"""
Project table model.

Canonical definition for ``love_engine_projecttable``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from datetime import datetime
from typing import List, Optional

from love_engine.models.budget import LOVE_ENGINE_BudgetTable
from love_engine.models.object_permission import LOVE_ENGINE_ObjectPermissionTable
from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_ProjectTable(LoveEnginePydanticObjectBase):
    """Database model representation for project"""

    project_id: str
    project_alias: Optional[str] = None
    description: Optional[str] = None
    team_id: Optional[str] = None
    budget_id: Optional[str] = None
    metadata: Optional[dict] = None
    models: List[str] = []
    spend: float = 0.0
    model_spend: Optional[dict] = None
    model_rpm_limit: Optional[dict] = None
    model_tpm_limit: Optional[dict] = None
    blocked: bool = False
    object_permission_id: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    love_engine_budget_table: Optional[LOVE_ENGINE_BudgetTable] = None
    object_permission: Optional[LOVE_ENGINE_ObjectPermissionTable] = None

    @property
    def is_blocked(self) -> bool:
        return self.blocked
