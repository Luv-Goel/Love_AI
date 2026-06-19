from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .lasso import LassoGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _lasso_callback = LassoGuardrail(
        guardrail_name=guardrail.get("guardrail_name", ""),
        api_key=love_engine_params.api_key,
        api_base=love_engine_params.api_base,
        user_id=love_engine_params.lasso_user_id,
        conversation_id=love_engine_params.lasso_conversation_id,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_lasso_callback)

    return _lasso_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.LASSO.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.LASSO.value: LassoGuardrail,
}
