"""Cisco AI Defense Guardrail Integration for LoveEngine."""

from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .cisco_ai_defense import (
    CiscoAIDefenseGuardrail,
    CiscoAIDefenseGuardrailAPIError,
    CiscoAIDefenseGuardrailMissingSecrets,
)

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("Cisco AI Defense: guardrail_name is required")

    optional_params = getattr(love_engine_params, "optional_params", None)

    _callback = CiscoAIDefenseGuardrail(
        guardrail_name=guardrail_name,
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        inspection_type=_get_optional_value(
            love_engine_params, optional_params, "inspection_type"
        ),
        inspect_path=_get_optional_value(
            love_engine_params, optional_params, "inspect_path"
        ),
        enabled_rules=_get_optional_value(
            love_engine_params, optional_params, "enabled_rules"
        ),
        integration_profile_id=_get_optional_value(
            love_engine_params, optional_params, "integration_profile_id"
        ),
        integration_profile_version=_get_optional_value(
            love_engine_params, optional_params, "integration_profile_version"
        ),
        integration_tenant_id=_get_optional_value(
            love_engine_params, optional_params, "integration_tenant_id"
        ),
        integration_type=_get_optional_value(
            love_engine_params, optional_params, "integration_type"
        ),
        on_flagged_action=_get_optional_value(
            love_engine_params, optional_params, "on_flagged_action"
        ),
        fallback_on_error=_get_optional_value(
            love_engine_params, optional_params, "fallback_on_error"
        ),
        timeout=_get_optional_value(love_engine_params, optional_params, "timeout"),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on or False,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_callback)

    # MCP post-tool-call hooks are dispatched through success callbacks.
    love_engine.logging_callback_manager.add_love_engine_success_callback(_callback)

    return _callback


def _get_optional_value(love_engine_params, optional_params, attribute_name):
    """Resolve Cisco optional params without inheriting sibling defaults."""
    if optional_params is not None:
        if isinstance(optional_params, dict):
            if attribute_name in optional_params:
                return optional_params[attribute_name]
        else:
            nested_fields_set = getattr(optional_params, "model_fields_set", None)
            if nested_fields_set is None or attribute_name in nested_fields_set:
                value = getattr(optional_params, attribute_name, None)
                if value is not None:
                    return value

    if love_engine_params is None:
        return None
    # Only accept flattened values the caller explicitly set.
    fields_set = getattr(love_engine_params, "model_fields_set", None)
    if fields_set is None or attribute_name not in fields_set:
        return None
    return getattr(love_engine_params, attribute_name, None)


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.CISCO_AI_DEFENSE.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.CISCO_AI_DEFENSE.value: CiscoAIDefenseGuardrail,
}


__all__ = [
    "CiscoAIDefenseGuardrail",
    "CiscoAIDefenseGuardrailAPIError",
    "CiscoAIDefenseGuardrailMissingSecrets",
    "initialize_guardrail",
    "guardrail_initializer_registry",
    "guardrail_class_registry",
]
