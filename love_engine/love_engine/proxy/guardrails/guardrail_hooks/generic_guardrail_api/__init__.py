from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .generic_guardrail_api import GenericGuardrailAPI

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _generic_guardrail_api_callback = GenericGuardrailAPI(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        headers=getattr(love_engine_params, "headers", None),
        additional_provider_specific_params=getattr(
            love_engine_params, "additional_provider_specific_params", {}
        ),
        unreachable_fallback=getattr(
            love_engine_params, "unreachable_fallback", "fail_closed"
        ),
        extra_headers=getattr(love_engine_params, "extra_headers", None),
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(
        _generic_guardrail_api_callback
    )
    return _generic_guardrail_api_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.GENERIC_GUARDRAIL_API.value: initialize_guardrail,
}

guardrail_class_registry = {
    SupportedGuardrailIntegrations.GENERIC_GUARDRAIL_API.value: GenericGuardrailAPI,
}
