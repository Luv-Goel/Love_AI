from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations

from .panw_prisma_airs import PanwPrismaAirsHandler

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    guardrail_name = guardrail.get("guardrail_name")

    # Note: api_key and profile_name can be None - handler will use env vars or API key's linked profile
    if not guardrail_name:
        raise ValueError("PANW Prisma AIRS: guardrail_name is required")

    _panw_callback = PanwPrismaAirsHandler(
        **{
            **love_engine_params.model_dump(exclude_unset=True),
            "guardrail_name": guardrail_name,
            "event_hook": love_engine_params.mode,
            "default_on": love_engine_params.default_on or False,
        }
    )
    love_engine.logging_callback_manager.add_love_engine_callback(_panw_callback)

    return _panw_callback


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.PANW_PRISMA_AIRS.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.PANW_PRISMA_AIRS.value: PanwPrismaAirsHandler,
}
