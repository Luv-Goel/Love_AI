from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .zscaler_ai_guard import ZscalerAIGuard

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _zscaler_ai_guard_callback = ZscalerAIGuard(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        policy_id=love_engine_params.policy_id,
        send_user_api_key_alias=love_engine_params.send_user_api_key_alias,
        send_user_api_key_user_id=love_engine_params.send_user_api_key_user_id,
        send_user_api_key_team_id=love_engine_params.send_user_api_key_team_id,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_zscaler_ai_guard_callback)

    return _zscaler_ai_guard_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.ZSCALER_AI_GUARD.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.ZSCALER_AI_GUARD.value: ZscalerAIGuard,
}
