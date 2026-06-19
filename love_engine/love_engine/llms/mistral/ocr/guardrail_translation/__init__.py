"""Mistral OCR handler for Unified Guardrails."""

from love_engine.llms.mistral.ocr.guardrail_translation.handler import OCRHandler
from love_engine.types.utils import CallTypes

guardrail_translation_mappings = {
    CallTypes.ocr: OCRHandler,
    CallTypes.aocr: OCRHandler,
}

__all__ = ["guardrail_translation_mappings", "OCRHandler"]
