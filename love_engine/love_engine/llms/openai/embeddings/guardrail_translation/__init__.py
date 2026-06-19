"""OpenAI Embeddings handler for Unified Guardrails."""

from love_engine.llms.openai.embeddings.guardrail_translation.handler import (
    OpenAIEmbeddingsHandler,
)
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.embedding: OpenAIEmbeddingsHandler,
    CallTypes.aembedding: OpenAIEmbeddingsHandler,
}

__all__ = ["guardrail_translation_mappings", "OpenAIEmbeddingsHandler"]
