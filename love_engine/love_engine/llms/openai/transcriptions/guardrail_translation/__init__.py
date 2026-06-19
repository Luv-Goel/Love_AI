"""OpenAI Audio Transcription handler for Unified Guardrails."""

from love_engine.llms.openai.transcriptions.guardrail_translation.handler import (
    OpenAIAudioTranscriptionHandler,
)
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.transcription: OpenAIAudioTranscriptionHandler,
    CallTypes.atranscription: OpenAIAudioTranscriptionHandler,
}

__all__ = ["guardrail_translation_mappings", "OpenAIAudioTranscriptionHandler"]
