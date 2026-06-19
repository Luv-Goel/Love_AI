from typing import TYPE_CHECKING

from love_engine.proxy.guardrails.guardrail_hooks.onyx.onyx import OnyxGuardrail
from love_engine.types.guardrails import SupportedGuardrailIntegrations

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _onyx_callback = OnyxGuardrail(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_onyx_callback)

    return _onyx_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.ONYX.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.ONYX.value: OnyxGuardrail,
}
