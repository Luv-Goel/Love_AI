"""
Tag table model.

Canonical definition for ``love_engine_tagtable``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import model_validator

from love_engine.models.budget import LOVE_ENGINE_BudgetTable
from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_TagTable(LoveEnginePydanticObjectBase):
    tag_name: str
    description: Optional[str] = None
    models: List[str] = []
    model_info: Optional[dict] = None
    spend: float = 0.0
    budget_id: Optional[str] = None
    love_engine_budget_table: Optional[LOVE_ENGINE_BudgetTable] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def set_model_info(cls, values):
        if values.get("spend") is None:
            values.update({"spend": 0.0})
        if values.get("models") is None:
            values.update({"models": []})
        return values
