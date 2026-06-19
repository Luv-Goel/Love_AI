"""
Semantic Guard guardrail — embedding-based prompt injection detection.

Uses semantic-router to match user prompts against known attack patterns.
"""

from typing import TYPE_CHECKING, Optional

import love_engine
from love_engine.constants import (
    DEFAULT_SEMANTIC_GUARD_EMBEDDING_MODEL,
    DEFAULT_SEMANTIC_GUARD_SIMILARITY_THRESHOLD,
)
from love_engine.proxy.guardrails.guardrail_hooks.semantic_guard.semantic_guard import (
    SemanticGuardrail,
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
    Initialize the Semantic Guard guardrail.

    Args:
        love_engine_params: Guardrail configuration parameters
        guardrail: Guardrail metadata
        llm_router: LoveEngine Router instance (required for embeddings)

    Returns:
        Initialized SemanticGuardrail instance
    """
    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("SemanticGuard: guardrail_name is required")

    if llm_router is None:
        raise ValueError(
            "SemanticGuard requires llm_router for embeddings. "
            "Configure a model_list with an embedding model."
        )

    semantic_guardrail = SemanticGuardrail(
        guardrail_name=guardrail_name,
        llm_router=llm_router,
        embedding_model=getattr(love_engine_params, "embedding_model", None)
        or DEFAULT_SEMANTIC_GUARD_EMBEDDING_MODEL,
        similarity_threshold=getattr(love_engine_params, "similarity_threshold", None)
        or DEFAULT_SEMANTIC_GUARD_SIMILARITY_THRESHOLD,
        route_templates=getattr(love_engine_params, "route_templates", None),
        custom_routes_file=getattr(love_engine_params, "custom_routes_file", None),
        custom_routes=getattr(love_engine_params, "custom_routes", None),
        on_flagged_action=getattr(love_engine_params, "on_flagged_action", "block"),
        event_hook=love_engine_params.mode,  # type: ignore
        default_on=love_engine_params.default_on or False,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(semantic_guardrail)

    return semantic_guardrail


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.SEMANTIC_GUARD.value: initialize_guardrail,
}

guardrail_class_registry = {
    SupportedGuardrailIntegrations.SEMANTIC_GUARD.value: SemanticGuardrail,
}
