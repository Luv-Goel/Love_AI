from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .hiddenlayer import HiddenlayerGuardrail, HiddenlayerGuardrailV2

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    api_id = love_engine_params.api_id if hasattr(love_engine_params, "api_id") else None
    auth_url = love_engine_params.auth_url if hasattr(love_engine_params, "auth_url") else None
    version: int | None = (
        love_engine_params.version if hasattr(love_engine_params, "version") else None
    )

    _hiddenlayer_callback: HiddenlayerGuardrail | HiddenlayerGuardrailV2
    if not version or version < 2:
        _hiddenlayer_callback = HiddenlayerGuardrail(
            api_base=love_engine_params.api_base,
            api_id=api_id,
            api_key=love_engine_params.api_key,
            auth_url=auth_url,
            guardrail_name=guardrail.get("guardrail_name", ""),
            event_hook=love_engine_params.mode,
            default_on=love_engine_params.default_on,
        )
    else:
        _hiddenlayer_callback = HiddenlayerGuardrailV2(
            api_base=love_engine_params.api_base,
            api_id=api_id,
            api_key=love_engine_params.api_key,
            auth_url=auth_url,
            guardrail_name=guardrail.get("guardrail_name", ""),
            event_hook=love_engine_params.mode,
            default_on=love_engine_params.default_on,
        )

    love_engine.logging_callback_manager.add_love_engine_callback(_hiddenlayer_callback)
    return _hiddenlayer_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.HIDDENLAYER.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.HIDDENLAYER.value: HiddenlayerGuardrail,
}
