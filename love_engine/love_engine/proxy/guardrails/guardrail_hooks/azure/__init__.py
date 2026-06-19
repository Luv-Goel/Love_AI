from typing import TYPE_CHECKING, Union

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .prompt_shield import AzureContentSafetyPromptShieldGuardrail
from .text_moderation import AzureContentSafetyTextModerationGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    if not love_engine_params.api_key:
        raise ValueError("Azure Content Safety: api_key is required")
    if not love_engine_params.api_base:
        raise ValueError("Azure Content Safety: api_base is required")

    azure_guardrail = love_engine_params.guardrail.split("/")[1]

    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("Azure Content Safety: guardrail_name is required")

    if azure_guardrail == "prompt_shield":
        azure_content_safety_guardrail: Union[
            AzureContentSafetyPromptShieldGuardrail,
            AzureContentSafetyTextModerationGuardrail,
        ] = AzureContentSafetyPromptShieldGuardrail(
            guardrail_name=guardrail_name,
            **{
                **love_engine_params.model_dump(exclude_none=True),
                "api_key": love_engine_params.api_key,
                "api_base": love_engine_params.api_base,
                "default_on": love_engine_params.default_on,
                "event_hook": love_engine_params.mode,
            },
        )
    elif azure_guardrail == "text_moderations":
        azure_content_safety_guardrail = AzureContentSafetyTextModerationGuardrail(
            guardrail_name=guardrail_name,
            **{
                **love_engine_params.model_dump(exclude_none=True),
                "api_key": love_engine_params.api_key,
                "api_base": love_engine_params.api_base,
                "default_on": love_engine_params.default_on,
                "event_hook": love_engine_params.mode,
            },
        )
    else:
        raise ValueError(
            f"Azure Content Safety: {azure_guardrail} is not a valid guardrail"
        )

    love_engine.logging_callback_manager.add_love_engine_callback(
        azure_content_safety_guardrail
    )
    return azure_content_safety_guardrail


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.AZURE_PROMPT_SHIELD.value: initialize_guardrail,
    SupportedGuardrailIntegrations.AZURE_TEXT_MODERATIONS.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.AZURE_PROMPT_SHIELD.value: AzureContentSafetyPromptShieldGuardrail,
    SupportedGuardrailIntegrations.AZURE_TEXT_MODERATIONS.value: AzureContentSafetyTextModerationGuardrail,
}
