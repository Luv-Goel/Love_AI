"""Cohere Rerank handler for Unified Guardrails."""

from love_engine.llms.cohere.rerank.guardrail_translation.handler import CohereRerankHandler
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.rerank: CohereRerankHandler,
    CallTypes.arerank: CohereRerankHandler,
}

__all__ = ["guardrail_translation_mappings", "CohereRerankHandler"]
