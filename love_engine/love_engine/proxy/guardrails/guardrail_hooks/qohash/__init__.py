from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .qohash import QostodianNexus

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _instance = QostodianNexus(
        api_base=love_engine_params.api_base,
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
        additional_provider_specific_params=love_engine_params.additional_provider_specific_params,
        extra_headers=getattr(love_engine_params, "extra_headers", None),
    )

    love_engine.logging_callback_manager.add_love_engine_callback(_instance)

    return _instance


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.QOSTODIAN_NEXUS.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.QOSTODIAN_NEXUS.value: QostodianNexus,
}
