"""OpenAI Text Completion handler for Unified Guardrails."""

from love_engine.llms.openai.completion.guardrail_translation.handler import (
    OpenAITextCompletionHandler,
)
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.text_completion: OpenAITextCompletionHandler,
    CallTypes.atext_completion: OpenAITextCompletionHandler,
}

__all__ = ["guardrail_translation_mappings", "OpenAITextCompletionHandler"]
