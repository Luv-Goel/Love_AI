"""
Team membership table model.

Canonical definition for ``love_engine_teammembership``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from typing import Optional, Union

from love_engine.models.budget import LOVE_ENGINE_BudgetTable, LOVE_ENGINE_BudgetTableFull
from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_TeamMembership(LoveEnginePydanticObjectBase):
    user_id: str
    team_id: str
    budget_id: Optional[str] = None
    spend: Optional[float] = 0.0
    total_spend: Optional[float] = 0.0
    love_engine_budget_table: Optional[
        Union[LOVE_ENGINE_BudgetTableFull, LOVE_ENGINE_BudgetTable]
    ] = None

    def safe_get_team_member_rpm_limit(self) -> Optional[int]:
        if self.love_engine_budget_table is not None:
            return self.love_engine_budget_table.rpm_limit
        return None

    def safe_get_team_member_tpm_limit(self) -> Optional[int]:
        if self.love_engine_budget_table is not None:
            return self.love_engine_budget_table.tpm_limit
        return None
