"""
A2A to love_engine Completion Bridge.

This module provides transformation between A2A protocol messages and
love_engine completion API, enabling any love_engine-supported provider to be
invoked via the A2A protocol.
"""

from love_engine.a2a_protocol.love_engine_completion_bridge.handler import (
    A2ACompletionBridgeHandler,
    handle_a2a_completion,
    handle_a2a_completion_streaming,
)
from love_engine.a2a_protocol.love_engine_completion_bridge.transformation import (
    A2ACompletionBridgeTransformation,
)

__all__ = [
    "A2ACompletionBridgeTransformation",
    "A2ACompletionBridgeHandler",
    "handle_a2a_completion",
    "handle_a2a_completion_streaming",
]
