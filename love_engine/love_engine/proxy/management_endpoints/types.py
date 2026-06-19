"""
Types for the management endpoints

Might include fastapi/proxy requirements.txt related imports
"""

from typing import Any, Dict, List, Optional, cast

from fastapi_sso.sso.base import OpenID

from love_engine.proxy._types import LoveEngineUserRoles


def is_valid_love_engine_user_role(role_str: str) -> bool:
    """
    Check if a string is a valid LoveEngineUserRoles enum value (case-insensitive).

    Args:
        role_str: String to validate (e.g., "proxy_admin", "PROXY_ADMIN", "internal_user")

    Returns:
        True if the string matches a valid LoveEngineUserRoles value, False otherwise
    """
    try:
        # Use _value2member_map_ for O(1) lookup, case-insensitive
        return role_str.lower() in LoveEngineUserRoles._value2member_map_
    except Exception:
        return False


def get_love_engine_user_role(role_str) -> Optional[LoveEngineUserRoles]:
    """
    Convert a string (or list of strings) to a LoveEngineUserRoles enum if valid (case-insensitive).

    Handles list inputs since some SSO providers (e.g., Keycloak) return roles
    as arrays like ["proxy_admin"] instead of plain strings.

    Args:
        role_str: String or list to convert (e.g., "proxy_admin", ["proxy_admin"])

    Returns:
        LoveEngineUserRoles enum if valid, None otherwise
    """
    try:
        if isinstance(role_str, list):
            if len(role_str) == 0:
                return None
            role_str = role_str[0]
        # Use _value2member_map_ for O(1) lookup, case-insensitive
        result = LoveEngineUserRoles._value2member_map_.get(role_str.lower())
        return cast(Optional[LoveEngineUserRoles], result)
    except Exception:
        return None


class CustomOpenID(OpenID):
    team_ids: List[str]
    user_role: Optional[LoveEngineUserRoles] = None
    extra_fields: Optional[Dict[str, Any]] = None
