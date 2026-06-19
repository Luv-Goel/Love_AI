"""
End-user table model.

Canonical definition for ``love_engine_endusertable``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from typing import Literal, Optional

from pydantic import ConfigDict, model_validator

from love_engine.models.budget import LOVE_ENGINE_BudgetTable
from love_engine.models.object_permission import LOVE_ENGINE_ObjectPermissionTable
from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_EndUserTable(LoveEnginePydanticObjectBase):
    user_id: str
    blocked: bool
    alias: Optional[str] = None
    spend: float = 0.0
    allowed_model_region: Optional[Literal["eu", "us"]] = None
    default_model: Optional[str] = None
    love_engine_budget_table: Optional[LOVE_ENGINE_BudgetTable] = None
    object_permission_id: Optional[str] = None
    object_permission: Optional[LOVE_ENGINE_ObjectPermissionTable] = None

    @model_validator(mode="before")
    @classmethod
    def set_model_info(cls, values):
        if values.get("spend") is None:
            values.update({"spend": 0.0})
        return values

    model_config = ConfigDict(protected_namespaces=())
