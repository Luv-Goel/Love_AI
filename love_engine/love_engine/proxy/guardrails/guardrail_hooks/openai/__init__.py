from typing import TYPE_CHECKING

import love_engine
from love_engine.proxy.guardrails.guardrail_hooks.openai.moderations import (
    OpenAIModerationGuardrail,
)
from love_engine.types.guardrails import SupportedGuardrailIntegrations

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("OpenAI Moderation: guardrail_name is required")

    optional_params = getattr(love_engine_params, "optional_params", None)

    openai_moderation_guardrail = OpenAIModerationGuardrail(
        guardrail_name=guardrail_name,
        **{
            **love_engine_params.model_dump(exclude_none=True),
            "api_key": love_engine_params.api_key,
            "api_base": love_engine_params.api_base,
            "default_on": love_engine_params.default_on,
            "event_hook": love_engine_params.mode,
            "model": love_engine_params.model,
            "streaming_end_of_stream_only": _get_config_value(
                love_engine_params, optional_params, "streaming_end_of_stream_only"
            ),
            "streaming_sampling_rate": _get_config_value(
                love_engine_params, optional_params, "streaming_sampling_rate"
            ),
        },
    )

    love_engine.logging_callback_manager.add_love_engine_callback(openai_moderation_guardrail)

    return openai_moderation_guardrail


def _get_config_value(love_engine_params, optional_params, attribute_name):
    if optional_params is not None:
        value = getattr(optional_params, attribute_name, None)
        if value is not None:
            return value
    return getattr(love_engine_params, attribute_name, None)


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.OPENAI_MODERATION.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.OPENAI_MODERATION.value: OpenAIModerationGuardrail,
}
