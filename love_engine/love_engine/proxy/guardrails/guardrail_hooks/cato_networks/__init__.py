from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .cato_networks import CatoNetworksGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine
    from love_engine.proxy.guardrails.guardrail_hooks.cato_networks import (
        CatoNetworksGuardrail,
    )

    _cato_callback = CatoNetworksGuardrail(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
        ssl_verify=getattr(love_engine_params, "ssl_verify", None),
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_cato_callback)

    return _cato_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.CATO_NETWORKS.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.CATO_NETWORKS.value: CatoNetworksGuardrail,
}
