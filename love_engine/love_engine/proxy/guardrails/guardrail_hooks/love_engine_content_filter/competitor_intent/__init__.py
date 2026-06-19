"""
Competitor intent: entity + intent disambiguation with safe (non-competitor) defaults.

Base logic in base.py; industry-specific checkers in submodules (e.g. airline.py).
"""

from love_engine.proxy.guardrails.guardrail_hooks.love_engine_content_filter.competitor_intent.airline import (
    AirlineCompetitorIntentChecker,
)
from love_engine.proxy.guardrails.guardrail_hooks.love_engine_content_filter.competitor_intent.base import (
    BaseCompetitorIntentChecker,
    normalize,
    text_for_entity_matching,
)

__all__ = [
    "BaseCompetitorIntentChecker",
    "AirlineCompetitorIntentChecker",
    "normalize",
    "text_for_entity_matching",
]
