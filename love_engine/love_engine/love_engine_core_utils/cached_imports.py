"""
Cached imports module for LoveEngine.

This module provides cached import functionality to avoid repeated imports
inside functions that are critical to performance.
"""

from typing import TYPE_CHECKING, Callable, Optional, Type

# Type annotations for cached imports
if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging
    from love_engine.love_engine_core_utils.coroutine_checker import CoroutineChecker

# Global cache variables
_LoveEngineLogging: Optional[Type["Logging"]] = None
_coroutine_checker: Optional["CoroutineChecker"] = None
_set_callbacks: Optional[Callable] = None


def get_love_engine_logging_class() -> Type["Logging"]:
    """Get the cached LoveEngine Logging class, initializing if needed."""
    global _LoveEngineLogging
    if _LoveEngineLogging is not None:
        return _LoveEngineLogging
    from love_engine.love_engine_core_utils.love_engine_logging import Logging

    _LoveEngineLogging = Logging
    return _LoveEngineLogging


def get_coroutine_checker() -> "CoroutineChecker":
    """Get the cached coroutine checker instance, initializing if needed."""
    global _coroutine_checker
    if _coroutine_checker is not None:
        return _coroutine_checker
    from love_engine.love_engine_core_utils.coroutine_checker import coroutine_checker

    _coroutine_checker = coroutine_checker
    return _coroutine_checker


def get_set_callbacks() -> Callable:
    """Get the cached set_callbacks function, initializing if needed."""
    global _set_callbacks
    if _set_callbacks is not None:
        return _set_callbacks
    from love_engine.love_engine_core_utils.love_engine_logging import set_callbacks

    _set_callbacks = set_callbacks
    return _set_callbacks


def clear_cached_imports() -> None:
    """Clear all cached imports. Useful for testing or memory management."""
    global _LoveEngineLogging, _coroutine_checker, _set_callbacks
    _LoveEngineLogging = None
    _coroutine_checker = None
    _set_callbacks = None
