from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .akto import AktoGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    _akto_callback = AktoGuardrail(
        akto_base_url=getattr(love_engine_params, "akto_base_url", None),
        akto_api_key=getattr(love_engine_params, "akto_api_key", None),
        akto_account_id=getattr(love_engine_params, "akto_account_id", None),
        akto_vxlan_id=getattr(love_engine_params, "akto_vxlan_id", None),
        unreachable_fallback=getattr(
            love_engine_params, "unreachable_fallback", "fail_closed"
        ),
        guardrail_timeout=getattr(love_engine_params, "guardrail_timeout", None),
        guardrail_name=guardrail.get("guardrail_name", ""),
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(_akto_callback)
    return _akto_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.AKTO.value: initialize_guardrail,
}

guardrail_class_registry = {
    SupportedGuardrailIntegrations.AKTO.value: AktoGuardrail,
}
