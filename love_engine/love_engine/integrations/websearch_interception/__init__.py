"""
WebSearch Interception Module

Provides server-side WebSearch tool execution for models that don't natively
support server-side tool calling (e.g., Bedrock/Claude).
"""

from love_engine.integrations.websearch_interception.handler import (
    WebSearchInterceptionLogger,
)
from love_engine.integrations.websearch_interception.tools import (
    get_love_engine_web_search_tool,
    is_web_search_tool,
)

__all__ = [
    "WebSearchInterceptionLogger",
    "get_love_engine_web_search_tool",
    "is_web_search_tool",
]
