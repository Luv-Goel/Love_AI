from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .guardrails_ai import GuardrailsAI

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    if love_engine_params.guard_name is None:
        raise Exception(
            "GuardrailsAIException - Please pass the Guardrails AI guard name via 'love_engine_params::guard_name'"
        )

    _guardrails_ai_callback = GuardrailsAI(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
        guard_name=love_engine_params.guard_name,
        guardrails_ai_api_input_format=getattr(
            love_engine_params, "guardrails_ai_api_input_format", "llmOutput"
        ),
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_guardrails_ai_callback)

    return _guardrails_ai_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.GUARDRAILS_AI.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.GUARDRAILS_AI.value: GuardrailsAI,
}
