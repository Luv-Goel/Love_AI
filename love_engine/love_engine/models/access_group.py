"""
Access group table model.

Canonical definition for ``love_engine_accessgrouptable``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from datetime import datetime
from typing import List, Optional

from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_AccessGroupTable(LoveEnginePydanticObjectBase):
    access_group_id: str
    access_group_name: str
    description: Optional[str] = None
    access_model_names: List[str] = []
    access_mcp_server_ids: List[str] = []
    access_agent_ids: List[str] = []
    assigned_team_ids: List[str] = []
    assigned_key_ids: List[str] = []
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
