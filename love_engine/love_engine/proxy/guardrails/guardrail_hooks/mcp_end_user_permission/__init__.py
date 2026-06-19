from typing import TYPE_CHECKING, Any, Dict, cast

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .mcp_end_user_permission import MCPEndUserPermissionGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    # Default to always-on. Only disable if the user explicitly sets default_on: false.
    # We check the raw guardrail dict because LoveEngineParams normalizes None → False,
    # making it impossible to distinguish "not set" from "explicitly false" via love_engine_params.
    _raw_default_on = (
        cast(Dict[str, Any], guardrail).get("love_engine_params", {}).get("default_on")
    )
    _default_on = False if _raw_default_on is False else True

    _callback = MCPEndUserPermissionGuardrail(
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=_default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_callback)
    return _callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.MCP_END_USER_PERMISSION.value: initialize_guardrail,
}

guardrail_class_registry = {
    SupportedGuardrailIntegrations.MCP_END_USER_PERMISSION.value: MCPEndUserPermissionGuardrail,
}
