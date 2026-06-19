from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .noma import NomaGuardrail
from .noma_v2 import NomaV2Guardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    use_v2 = getattr(love_engine_params, "use_v2", False)
    if isinstance(use_v2, str):
        use_v2 = use_v2.lower() == "true"
    if use_v2:
        return initialize_guardrail_v2(
            love_engine_params=love_engine_params, guardrail=guardrail
        )

    import love_engine

    _noma_callback = NomaGuardrail(
        guardrail_name=guardrail.get("guardrail_name", ""),
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        application_id=love_engine_params.application_id,
        monitor_mode=love_engine_params.monitor_mode,
        block_failures=love_engine_params.block_failures,
        anonymize_input=love_engine_params.anonymize_input,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_noma_callback)

    return _noma_callback


def initialize_guardrail_v2(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _noma_v2_callback = NomaV2Guardrail(
        guardrail_name=guardrail.get("guardrail_name", ""),
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        application_id=love_engine_params.application_id,
        monitor_mode=love_engine_params.monitor_mode,
        block_failures=love_engine_params.block_failures,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_noma_v2_callback)

    return _noma_v2_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.NOMA.value: initialize_guardrail,
    SupportedGuardrailIntegrations.NOMA_V2.value: initialize_guardrail_v2,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.NOMA.value: NomaGuardrail,
    SupportedGuardrailIntegrations.NOMA_V2.value: NomaV2Guardrail,
}
