from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .vigil_guard import VigilGuardGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _vigil_guard_callback = VigilGuardGuardrail(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        unreachable_fallback=love_engine_params.unreachable_fallback,
        timeout=love_engine_params.timeout,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_vigil_guard_callback)
    return _vigil_guard_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.VIGIL_GUARD.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.VIGIL_GUARD.value: VigilGuardGuardrail,
}
