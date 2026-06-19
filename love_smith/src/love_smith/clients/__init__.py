"""Client adapters for LLM backends."""

from love_smith.clients.base import ChunkType, LLMClient, StreamChunk
from love_smith.clients.llamafile import LlamafileClient
from love_smith.clients.ollama import OllamaClient
from love_smith.clients.openai_compat import OpenAICompatClient
from love_smith.clients.vllm import VLLMClient
from love_smith.clients.sampling_defaults import (
    MODEL_SAMPLING_DEFAULTS,
    apply_sampling_defaults,
    get_sampling_defaults,
)

__all__ = [
    "ChunkType",
    "LLMClient",
    "LlamafileClient",
    "MODEL_SAMPLING_DEFAULTS",
    "OllamaClient",
    "OpenAICompatClient",
    "StreamChunk",
    "VLLMClient",
    "apply_sampling_defaults",
    "get_sampling_defaults",
]
