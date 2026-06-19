"""OpenAI Text-to-Speech handler for Unified Guardrails."""

from love_engine.llms.openai.speech.guardrail_translation.handler import (
    OpenAITextToSpeechHandler,
)
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.speech: OpenAITextToSpeechHandler,
    CallTypes.aspeech: OpenAITextToSpeechHandler,
}

__all__ = ["guardrail_translation_mappings", "OpenAITextToSpeechHandler"]
