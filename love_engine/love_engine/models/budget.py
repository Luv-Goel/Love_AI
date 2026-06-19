"""
Budget table model.

Canonical definition for ``love_engine_budgettable``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict

from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_BudgetTable(LoveEnginePydanticObjectBase):
    """Represents user-controllable params for a LOVE_ENGINE_BudgetTable record.

    Budget-write paths use `model_fields.keys()` on this class as an allowlist
    for user input. Keep server-managed fields (e.g. `budget_reset_at`) on
    `LOVE_ENGINE_BudgetTableFull` so they aren't user-settable.
    """

    budget_id: Optional[str] = None
    soft_budget: Optional[float] = None
    max_budget: Optional[float] = None
    max_parallel_requests: Optional[int] = None
    tpm_limit: Optional[int] = None
    rpm_limit: Optional[int] = None
    model_max_budget: Optional[dict] = None
    budget_duration: Optional[str] = None
    allowed_models: Optional[List[str]] = (
        None  # per-member model scope; empty = inherit team models
    )

    model_config = ConfigDict(protected_namespaces=())


class LOVE_ENGINE_BudgetTableFull(LOVE_ENGINE_BudgetTable):
    """LOVE_ENGINE_BudgetTable + server-managed fields returned on API responses."""

    budget_reset_at: Optional[datetime] = None
    created_at: datetime


class LOVE_ENGINE_TeamMemberTable(LOVE_ENGINE_BudgetTable):
    """
    Used to track spend of a user_id within a team_id
    """

    spend: Optional[float] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    budget_id: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=())
