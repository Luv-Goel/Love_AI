from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .qualifire import QualifireGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _qualifire_callback = QualifireGuardrail(
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        evaluation_id=getattr(love_engine_params, "evaluation_id", None),
        prompt_injections=getattr(love_engine_params, "prompt_injections", None),
        hallucinations_check=getattr(love_engine_params, "hallucinations_check", None),
        grounding_check=getattr(love_engine_params, "grounding_check", None),
        pii_check=getattr(love_engine_params, "pii_check", None),
        content_moderation_check=getattr(
            love_engine_params, "content_moderation_check", None
        ),
        tool_selection_quality_check=getattr(
            love_engine_params, "tool_selection_quality_check", None
        ),
        assertions=getattr(love_engine_params, "assertions", None),
        on_flagged=getattr(love_engine_params, "on_flagged", "block"),
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(_qualifire_callback)

    return _qualifire_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.QUALIFIRE.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.QUALIFIRE.value: QualifireGuardrail,
}
