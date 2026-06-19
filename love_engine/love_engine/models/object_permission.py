"""
Object permission table model.

Canonical definition for ``love_engine_objectpermissiontable``. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from typing import Dict, List, Optional

from love_engine.types.llms.base import LoveEnginePydanticObjectBase


class LOVE_ENGINE_ObjectPermissionTable(LoveEnginePydanticObjectBase):
    """Represents a LOVE_ENGINE_ObjectPermissionTable record"""

    object_permission_id: str
    mcp_servers: Optional[List[str]] = []
    mcp_access_groups: Optional[List[str]] = []
    mcp_tool_permissions: Optional[Dict[str, List[str]]] = None
    vector_stores: Optional[List[str]] = []
    agents: Optional[List[str]] = []
    agent_access_groups: Optional[List[str]] = []
    models: Optional[List[str]] = []
    mcp_toolsets: Optional[List[str]] = None
    blocked_tools: Optional[List[str]] = []
    search_tools: Optional[List[str]] = []
