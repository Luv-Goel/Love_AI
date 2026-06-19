"""love_smith — a reusable framework for self-hosted LLM tool-calling and multi-step agentic workflows."""

from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:
    __version__ = _pkg_version("love_smith-guardrails")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

from love_smith.core.messages import Message, MessageMeta, MessageRole, MessageType, ToolCallInfo
from love_smith.core.workflow import (
    LLMResponse,
    TextResponse,
    ToolCall,
    ToolDef,
    ToolSpec,
    Workflow,
)
from love_smith.core.steps import StepTracker
from love_smith.core.inference import (
    InferenceResult,
    fold_and_serialize,
    prepare_backend_messages,
    run_inference,
)
from love_smith.core.reasoning import DEFAULT_REASONING_REPLAY, REASONING_REPLAY_CHOICES, ReasoningReplay
from love_smith.core.runner import WorkflowRunner
from love_smith.core.slot_worker import SlotWorker
from love_smith.clients.base import ChunkType, LLMClient, StreamChunk, TokenUsage
from love_smith.clients.llamafile import LlamafileClient
from love_smith.clients.ollama import OllamaClient
from love_smith.clients.openai_compat import OpenAICompatClient
from love_smith.clients.vllm import VLLMClient
from love_smith.context import (
    CompactEvent,
    CompactStrategy,
    ContextManager,
    HardwareProfile,
    NoCompact,
    SlidingWindowCompact,
    TieredCompact,
    default_context_warning,
    detect_hardware,
)
from love_smith.server import BudgetMode, ServerManager, setup_backend
from love_smith.tools import RESPOND_TOOL_NAME, respond_spec, respond_tool
from love_smith.prompts import build_tool_prompt, extract_tool_call, rescue_tool_call, retry_nudge, step_nudge
from love_smith.guardrails import (
    CheckResult,
    ErrorTracker,
    Guardrails,
    Nudge,
    ResponseValidator,
    StepCheck,
    StepEnforcer,
    ValidationResult,
)
from love_smith.errors import (
    BudgetResolutionError,
    ContextBudgetExceeded,
    ContextDiscoveryError,
    love_smithError,
    HardwareDetectionError,
    MaxIterationsError,
    PrerequisiteError,
    StepEnforcementError,
    StreamError,
    ThinkingNotSupportedError,
    ToolCallError,
    ToolExecutionError,
    ToolResolutionError,
    WorkflowCancelledError,
)

__all__ = [
    # Version
    "__version__",
    # Messages
    "Message",
    "MessageMeta",
    "MessageRole",
    "MessageType",
    "ToolCallInfo",
    # Tools & Workflow
    "LLMResponse",
    "TextResponse",
    "ToolCall",
    "ToolDef",
    "ToolSpec",
    "Workflow",
    # Steps
    "StepTracker",
    # Inference (front half — shared by runner and proxy)
    "InferenceResult",
    "fold_and_serialize",
    "prepare_backend_messages",
    "run_inference",
    "DEFAULT_REASONING_REPLAY",
    "REASONING_REPLAY_CHOICES",
    "ReasoningReplay",
    # Runner
    "WorkflowRunner",
    # Slot worker
    "SlotWorker",
    # Client
    "ChunkType",
    "LLMClient",
    "LlamafileClient",
    "OllamaClient",
    "OpenAICompatClient",
    "VLLMClient",
    "StreamChunk",
    "TokenUsage",
    # Context
    "CompactEvent",
    "CompactStrategy",
    "ContextManager",
    "default_context_warning",
    "HardwareProfile",
    "NoCompact",
    "SlidingWindowCompact",
    "TieredCompact",
    "detect_hardware",
    # Prompts
    "build_tool_prompt",
    "extract_tool_call",
    "rescue_tool_call",
    "retry_nudge",
    "step_nudge",
    # Server
    "BudgetMode",
    "ServerManager",
    "setup_backend",
    # Built-in tools
    "RESPOND_TOOL_NAME",
    "respond_spec",
    "respond_tool",
    # Guardrails
    "CheckResult",
    "Guardrails",
    # Guardrails (granular middleware)
    "ErrorTracker",
    "Nudge",
    "ResponseValidator",
    "StepCheck",
    "StepEnforcer",
    "ValidationResult",
    # Errors
    "BudgetResolutionError",
    "ContextBudgetExceeded",
    "ContextDiscoveryError",
    "love_smithError",
    "HardwareDetectionError",
    "MaxIterationsError",
    "PrerequisiteError",
    "StepEnforcementError",
    "StreamError",
    "ThinkingNotSupportedError",
    "ToolCallError",
    "ToolExecutionError",
    "ToolResolutionError",
    "WorkflowCancelledError",
]
