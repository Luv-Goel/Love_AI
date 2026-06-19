"""Context management for the love_smith library.

Provides compaction strategies, context budget management, and
hardware detection for VRAM-based budget estimation.
"""

from love_smith.context.hardware import (
    HardwareProfile,
    detect_hardware,
)
from love_smith.context.manager import CompactEvent, ContextManager, default_context_warning
from love_smith.context.strategies import (
    CompactStrategy,
    NoCompact,
    SlidingWindowCompact,
    TieredCompact,
)

__all__ = [
    "CompactEvent",
    "CompactStrategy",
    "ContextManager",
    "default_context_warning",
    "HardwareProfile",
    "NoCompact",
    "SlidingWindowCompact",
    "TieredCompact",
    "detect_hardware",
]
