"""
love_engine Interactions API

This module provides SDK methods for Google's Interactions API.

Usage:
    import love_engine

    # Create an interaction with a model
    response = love_engine.interactions.create(
        model="gemini-2.5-flash",
        input="Hello, how are you?"
    )

    # Create an interaction with an agent
    response = love_engine.interactions.create(
        agent="deep-research-pro-preview-12-2025",
        input="Research the current state of cancer research"
    )

    # Async version
    response = await love_engine.interactions.acreate(...)

    # Get an interaction
    response = love_engine.interactions.get(interaction_id="...")

    # Delete an interaction
    result = love_engine.interactions.delete(interaction_id="...")

    # Cancel an interaction
    result = love_engine.interactions.cancel(interaction_id="...")

    # Create a managed agent on the provider side
    result = love_engine.interactions.agents.create(
        name="waverunner",
        custom_llm_provider="gemini",
        api_key="...",
        base_agent="gemini-2.5-flash",
        instructions="You are a helpful assistant.",
    )

Methods:
- create(): Sync create interaction
- acreate(): Async create interaction
- get(): Sync get interaction
- aget(): Async get interaction
- delete(): Sync delete interaction
- adelete(): Async delete interaction
- cancel(): Sync cancel interaction
- acancel(): Async cancel interaction

Sub-modules:
- agents: Provider-side agent creation (love_engine.interactions.agents.create)
"""

from love_engine.interactions import agents
from love_engine.interactions.main import (
    acancel,
    acreate,
    adelete,
    aget,
    cancel,
    create,
    delete,
    get,
)

__all__ = [
    # Create
    "create",
    "acreate",
    # Get
    "get",
    "aget",
    # Delete
    "delete",
    "adelete",
    # Cancel
    "cancel",
    "acancel",
    # Sub-modules
    "agents",
]
