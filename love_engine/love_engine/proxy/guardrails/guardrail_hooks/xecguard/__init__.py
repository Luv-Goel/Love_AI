from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .xecguard import XecGuardGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(
    love_engine_params: "LoveEngineParams",
    guardrail: "Guardrail",
):
    import love_engine

    _cb = XecGuardGuardrail(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        xecguard_model=love_engine_params.xecguard_model,
        policy_names=love_engine_params.policy_names,
        block_on_error=love_engine_params.block_on_error,
        grounding_strictness=love_engine_params.grounding_strictness,
        guardrail_name=guardrail.get(
            "guardrail_name",
            "",
        ),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(
        _cb,
    )

    return _cb


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.XECGUARD.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.XECGUARD.value: XecGuardGuardrail,
}
