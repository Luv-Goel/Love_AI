"""Pass-Through Endpoint guardrail translation handler."""

from love_engine.llms.pass_through.guardrail_translation.handler import (
    LlmPassthroughRouteHandler,
    PassThroughEndpointHandler,
)
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.pass_through: PassThroughEndpointHandler,
    CallTypes.allm_passthrough_route: LlmPassthroughRouteHandler,
}

__all__ = [
    "guardrail_translation_mappings",
    "LlmPassthroughRouteHandler",
    "PassThroughEndpointHandler",
]
