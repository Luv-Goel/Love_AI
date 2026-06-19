from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .prompt_security import PromptSecurityGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine
    from love_engine.proxy.guardrails.guardrail_hooks.prompt_security import (
        PromptSecurityGuardrail,
    )

    _prompt_security_callback = PromptSecurityGuardrail(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_prompt_security_callback)

    return _prompt_security_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.PROMPT_SECURITY.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.PROMPT_SECURITY.value: PromptSecurityGuardrail,
}
