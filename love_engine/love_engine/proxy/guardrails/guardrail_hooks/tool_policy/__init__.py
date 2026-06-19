import love_engine
from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: LoveEngineParams, guardrail: Guardrail):
    from love_engine.proxy.guardrails.guardrail_hooks.tool_policy.tool_policy_guardrail import (
        ToolPolicyGuardrail,
    )

    _callback = ToolPolicyGuardrail(
        guardrail_name=guardrail.get("guardrail_name", "tool_policy"),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_callback)
    return _callback
