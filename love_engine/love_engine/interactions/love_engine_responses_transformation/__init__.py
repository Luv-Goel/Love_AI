"""
Bridge module for connecting Interactions API to Responses API via love_engine.responses().
"""

from love_engine.interactions.love_engine_responses_transformation.handler import (
    LoveEngineResponsesInteractionsHandler,
)
from love_engine.interactions.love_engine_responses_transformation.transformation import (
    LoveEngineResponsesInteractionsConfig,
)

__all__ = [
    "LoveEngineResponsesInteractionsHandler",
    "LoveEngineResponsesInteractionsConfig",  # Transformation config class (not BaseInteractionsAPIConfig)
]
