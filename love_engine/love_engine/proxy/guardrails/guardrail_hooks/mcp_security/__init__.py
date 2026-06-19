from typing import TYPE_CHECKING, Literal, Optional, cast

import love_engine
from love_engine.proxy.guardrails.guardrail_hooks.mcp_security.mcp_security_guardrail import (
    MCPSecurityGuardrail,
)
from love_engine.types.guardrails import SupportedGuardrailIntegrations

if TYPE_CHECKING:
    from love_engine import Router
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(
    love_engine_params: "LoveEngineParams",
    guardrail: "Guardrail",
    llm_router: Optional["Router"] = None,
):
    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("MCP Security: guardrail_name is required")

    on_violation: Literal["block", "alert"] = cast(
        Literal["block", "alert"],
        getattr(love_engine_params, "on_violation", "block"),
    )

    mcp_security_guardrail = MCPSecurityGuardrail(
        guardrail_name=guardrail_name,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on or False,
        on_violation=on_violation,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(mcp_security_guardrail)
    return mcp_security_guardrail


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.MCP_SECURITY.value: initialize_guardrail,
}

guardrail_class_registry = {
    SupportedGuardrailIntegrations.MCP_SECURITY.value: MCPSecurityGuardrail,
}
