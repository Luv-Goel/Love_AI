from typing import TYPE_CHECKING, Optional

import love_engine
from love_engine.proxy.guardrails.guardrail_hooks.love_engine_content_filter.content_filter import (
    ContentFilterGuardrail,
)
from love_engine.types.guardrails import SupportedGuardrailIntegrations

if TYPE_CHECKING:
    from love_engine import Router
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(
    love_engine_params: "LoveEngineParams",
    guardrail: "Guardrail",
    llm_router: Optional["Router"] = None,
):
    """
    Initialize the Content Filter Guardrail.

    Args:
        love_engine_params: Guardrail configuration parameters
        guardrail: Guardrail metadata

    Returns:
        Initialized ContentFilterGuardrail instance
    """
    guardrail_name = guardrail.get("guardrail_name")

    if not guardrail_name:
        raise ValueError("Content Filter: guardrail_name is required")

    content_filter_guardrail = ContentFilterGuardrail(
        guardrail_name=guardrail_name,
        guardrail_id=guardrail.get("guardrail_id"),
        policy_template=guardrail.get("policy_template"),
        patterns=love_engine_params.patterns,
        blocked_words=love_engine_params.blocked_words,
        blocked_words_file=love_engine_params.blocked_words_file,
        event_hook=love_engine_params.mode,  # type: ignore
        default_on=love_engine_params.default_on or False,
        categories=getattr(love_engine_params, "categories", None),
        severity_threshold=getattr(love_engine_params, "severity_threshold", "medium"),
        llm_router=llm_router,
        image_model=getattr(love_engine_params, "image_model", None),
        competitor_intent_config=getattr(
            love_engine_params, "competitor_intent_config", None
        ),
        end_session_after_n_fails=getattr(
            love_engine_params, "end_session_after_n_fails", None
        ),
        on_violation=getattr(love_engine_params, "on_violation", None),
        realtime_violation_message=getattr(
            love_engine_params, "realtime_violation_message", None
        ),
    )

    love_engine.logging_callback_manager.add_love_engine_callback(content_filter_guardrail)

    return content_filter_guardrail


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.LOVE_ENGINE_CONTENT_FILTER.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.LOVE_ENGINE_CONTENT_FILTER.value: ContentFilterGuardrail,
}
