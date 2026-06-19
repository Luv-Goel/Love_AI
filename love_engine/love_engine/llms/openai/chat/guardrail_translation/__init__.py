"""OpenAI Chat Completions message handler for Unified Guardrails."""

from love_engine.llms.openai.chat.guardrail_translation.handler import (
    OpenAIChatCompletionsHandler,
)
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.completion: OpenAIChatCompletionsHandler,
    CallTypes.acompletion: OpenAIChatCompletionsHandler,
}
__all__ = ["guardrail_translation_mappings"]
