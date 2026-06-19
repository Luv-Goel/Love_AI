from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .pangea import PangeaHandler

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("Pangea guardrail name is required")

    _pangea_callback = PangeaHandler(
        guardrail_name=guardrail_name,
        pangea_input_recipe=love_engine_params.pangea_input_recipe,
        pangea_output_recipe=love_engine_params.pangea_output_recipe,
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_pangea_callback)

    return _pangea_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.PANGEA.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.PANGEA.value: PangeaHandler,
}
