"""Custom code guardrail integration for LoveEngine.

This module allows users to write custom guardrail logic using Python-like code
that runs in a sandboxed environment with access to LoveEngine-provided primitives.

Pre-built custom code for common guardrails (e.g. response rejection detection)
is available in response_rejection_code.py.
"""

from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .custom_code_guardrail import CustomCodeGuardrail
from .response_rejection_code import (
    DEFAULT_REJECTION_PHRASES,
    RESPONSE_REJECTION_GUARDRAIL_CODE,
)

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(
    love_engine_params: "LoveEngineParams", guardrail: "Guardrail"
) -> CustomCodeGuardrail:
    """
    Initialize a custom code guardrail.

    Args:
        love_engine_params: Configuration parameters including the custom code
        guardrail: The guardrail configuration dict

    Returns:
        CustomCodeGuardrail instance
    """
    import love_engine

    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("Custom code guardrail requires a guardrail_name")

    # Get the custom code from love_engine_params
    custom_code = getattr(love_engine_params, "custom_code", None)
    if not custom_code:
        raise ValueError(
            "Custom code guardrail requires 'custom_code' in love_engine_params"
        )

    custom_code_guardrail = CustomCodeGuardrail(
        guardrail_name=guardrail_name,
        custom_code=custom_code,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(custom_code_guardrail)
    return custom_code_guardrail


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.CUSTOM_CODE.value: initialize_guardrail,
}

guardrail_class_registry = {
    SupportedGuardrailIntegrations.CUSTOM_CODE.value: CustomCodeGuardrail,
}

__all__ = [
    "CustomCodeGuardrail",
    "DEFAULT_REJECTION_PHRASES",
    "RESPONSE_REJECTION_GUARDRAIL_CODE",
    "initialize_guardrail",
]
