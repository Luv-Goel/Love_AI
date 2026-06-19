from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .javelin import JavelinGuardrail

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    if love_engine_params.guard_name is None:
        raise Exception(
            "JavelinGuardrailException - Please pass the Javelin guard name via 'love_engine_params::guard_name'"
        )

    _javelin_callback = JavelinGuardrail(
        api_base=love_engine_params.api_base,
        api_key=love_engine_params.api_key,
        guardrail_name=guardrail.get("guardrail_name", ""),
        javelin_guard_name=love_engine_params.guard_name,
        event_hook=love_engine_params.mode,
        default_on=love_engine_params.default_on or False,
        api_version=love_engine_params.api_version or "v1",
        config=love_engine_params.config,
        metadata=love_engine_params.metadata,
        application=love_engine_params.application,
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_javelin_callback)

    return _javelin_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.JAVELIN.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.JAVELIN.value: JavelinGuardrail,
}
