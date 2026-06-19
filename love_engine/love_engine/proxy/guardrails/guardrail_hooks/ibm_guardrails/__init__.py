from typing import TYPE_CHECKING

from love_engine.types.guardrails import SupportedGuardrailIntegrations
from love_engine.types.proxy.guardrails.guardrail_hooks.ibm import IBMDetectorOptionalParams

from .ibm_detector import IBMGuardrailDetector

if TYPE_CHECKING:
    from love_engine.types.guardrails import Guardrail, LoveEngineParams


def initialize_guardrail(love_engine_params: "LoveEngineParams", guardrail: "Guardrail"):
    import love_engine

    if not love_engine_params.auth_token:
        raise ValueError("IBM Guardrails: auth_token is required")
    if not love_engine_params.base_url:
        raise ValueError("IBM Guardrails: base_url is required")
    if not love_engine_params.detector_id:
        raise ValueError("IBM Guardrails: detector_id is required")

    guardrail_name = guardrail.get("guardrail_name")
    if not guardrail_name:
        raise ValueError("IBM Guardrails: guardrail_name is required")

    verify_ssl = getattr(love_engine_params, "verify_ssl", True)

    # Get optional params
    optional_params = getattr(
        love_engine_params, "optional_params", IBMDetectorOptionalParams()
    )
    detector_params = getattr(optional_params, "detector_params", {})
    extra_headers = getattr(optional_params, "extra_headers", {})
    score_threshold = getattr(optional_params, "score_threshold", None)
    block_on_detection = getattr(optional_params, "block_on_detection", True)

    is_detector_server = love_engine_params.is_detector_server
    if is_detector_server is None:
        is_detector_server = True

    ibm_guardrail = IBMGuardrailDetector(
        guardrail_name=guardrail_name,
        auth_token=love_engine_params.auth_token,
        base_url=love_engine_params.base_url,
        detector_id=love_engine_params.detector_id,
        is_detector_server=is_detector_server,
        detector_params=detector_params,
        extra_headers=extra_headers,
        score_threshold=score_threshold,
        block_on_detection=block_on_detection,
        verify_ssl=verify_ssl,
        default_on=love_engine_params.default_on,
        event_hook=love_engine_params.mode,
    )

    love_engine.logging_callback_manager.add_love_engine_callback(ibm_guardrail)
    return ibm_guardrail


guardrail_initializer_registry = {
    SupportedGuardrailIntegrations.IBM_GUARDRAILS.value: initialize_guardrail,
}


guardrail_class_registry = {
    SupportedGuardrailIntegrations.IBM_GUARDRAILS.value: IBMGuardrailDetector,
}


__all__ = ["IBMGuardrailDetector", "initialize_guardrail"]
