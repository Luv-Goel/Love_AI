"""
Pillar Security Guardrail Integration for LoveEngine
"""

from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .pillar import (
    PillarGuardrail,
    PillarGuardrailAPIError,
    PillarGuardrailMissingSecrets,
)

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("Pillar guardrail name is required")

    optional_params = getattr(love_engine_params, "optional_params", None)

    _pillar_callback = PillarGuardrail(
        guardrail_name=guardrail_name,
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        on_flagged_action=getattr(love_engine_params, "on_flagged_action", "monitor"),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
        async_mode=_get_config_value(love_engine_params, optional_params, "async_mode"),
        persist_session=_get_config_value(
            love_engine_params, optional_params, "persist_session"
        ),
        include_scanners=_get_config_value(
            love_engine_params, optional_params, "include_scanners"
        ),
        include_evidence=_get_config_value(
            love_engine_params, optional_params, "include_evidence"
        ),
        fallback_on_error=_get_config_value(
            love_engine_params, optional_params, "fallback_on_error"
        ),
        timeout=_get_config_value(love_engine_params, optional_params, "timeout"),
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_pillar_callback)

    return _pillar_callback


def _get_config_value(love_engine_params, optional_params, attribute_name):
    """Return guardrail configuration value prioritising optional params when present."""

    if optional_params is not None:
        value = getattr(optional_params, attribute_name, None)
        if value is not None:
            return value
    return getattr(love_engine_params, attribute_name, None)


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.PILLAR.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.PILLAR.value: PillarGuardrail,
}

__all__ = [
    "PillarGuardrail",
    "PillarGuardrailAPIError",
    "PillarGuardrailMissingSecrets",
]
