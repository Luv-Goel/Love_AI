"""A2A Protocol handler for Unified Guardrails."""

from love_engine.llms.a2a.chat.guardrail_translation.handler import A2AGuardrailHandler
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.send_message: A2AGuardrailHandler,
    CallTypes.asend_message: A2AGuardrailHandler,
}

__all__ = ["guardrail_translation_mappings"]
