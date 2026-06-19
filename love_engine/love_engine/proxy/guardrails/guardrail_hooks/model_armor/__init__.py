from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .model_armor import ModelArmorGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine
    from love_engine.proxy.guardrails.guardrail_hooks.model_armor import (
        ModelArmorGuardrail,
    )

    _model_armor_callback = ModelArmorGuardrail(
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        template_id=love_engine_params.template_id,
        project_id=love_engine_params.project_id,
        location=love_engine_params.location,
        credentials=love_engine_params.credentials,
        api_endpoint=love_engine_params.api_endpoint,
        default_on=love_engine_params.default_on,
        mask_request_content=love_engine_params.mask_request_content,
        mask_response_content=love_engine_params.mask_response_content,
        fail_on_error=love_engine_params.fail_on_error,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_model_armor_callback)

    return _model_armor_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.MODEL_ARMOR.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.MODEL_ARMOR.value: ModelArmorGuardrail,
}
