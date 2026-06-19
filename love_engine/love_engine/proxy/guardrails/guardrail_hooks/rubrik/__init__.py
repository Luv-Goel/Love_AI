"""Rubrik guardrail integration for LoveEngine."""

from typing import TYPE_CHECKING

from love_engine.integrations.rubrik import RubrikLogger
from love_engine.types.guardrails import SupportedGuardrailIntegrations

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(
    love_engine_params: "LoveEngineParams", guardrail: "Guardrail"
) -> RubrikLogger:
    import love_engine

    rubrik_callback = RubrikLogger(
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(rubrik_callback)
    return rubrik_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.RUBRIK.value: initialize_guardrail,
}

guardrail_class_registry = {
    SupportedGuardrailIntegrations.RUBRIK.value: RubrikLogger,
}
