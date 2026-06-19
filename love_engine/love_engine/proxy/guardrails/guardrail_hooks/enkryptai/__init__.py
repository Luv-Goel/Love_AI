from .enkryptai import EnkryptAIGuardrails

__all__ = ["EnkryptAIGuardrails"]


from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _enkryptai_callback = EnkryptAIGuardrails(
        guardrail_name=guardrail.get("guardrail_name", ""),
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        policy_name=love_engine_params.policy_name,
        deployment_name=love_engine_params.deployment_name,
        detectors=love_engine_params.detectors,
        block_on_violation=love_engine_params.block_on_violation,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_enkryptai_callback)

    return _enkryptai_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.ENKRYPTAI.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.ENKRYPTAI.value: EnkryptAIGuardrails,
}
