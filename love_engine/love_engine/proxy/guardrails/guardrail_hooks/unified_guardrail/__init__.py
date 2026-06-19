from love_engine.llms.openai.chat.guardrail_translation.handler import (
    OpenAIChatCompletionsHandler,
)
from love_engine.types.utils import CallTypes

endpoint_translation_mappings = {
    CallTypes.completion: OpenAIChatCompletionsHandler,
    CallTypes.acompletion: OpenAIChatCompletionsHandler,
}

__all__ = ["endpoint_translation_mappings"]
