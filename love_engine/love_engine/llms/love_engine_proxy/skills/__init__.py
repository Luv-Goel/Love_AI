"""
love_engine Proxy Skills - Database-backed skills storage and execution

This module provides:
- Database-backed skills storage (alternative to Anthropic's cloud-based skills API)
- Skill content extraction and prompt injection
- Sandboxed code execution for skills
- Automatic code execution handler

Main components:
- handler.py: LoveEngineSkillsHandler - database CRUD operations
- transformation.py: LoveEngineSkillsTransformationHandler - SDK transformation layer
- prompt_injection.py: SkillPromptInjectionHandler - SKILL.md extraction and injection
- sandbox_executor.py: SkillsSandboxExecutor - Docker sandbox execution
- code_execution.py: CodeExecutionHandler - automatic agentic loop
"""

from love_engine.llms.love_engine_proxy.skills.code_execution import (
    LOVE_ENGINE_CODE_EXECUTION_TOOL,
    CodeExecutionHandler,
    LoveEngineInternalTools,
    add_code_execution_tool,
    code_execution_handler,
    get_love_engine_code_execution_tool,
    has_code_execution_tool,
)
from love_engine.llms.love_engine_proxy.skills.constants import (
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_SANDBOX_TIMEOUT,
)
from love_engine.llms.love_engine_proxy.skills.handler import LoveEngineSkillsHandler
from love_engine.llms.love_engine_proxy.skills.prompt_injection import (
    SkillPromptInjectionHandler,
)
from love_engine.llms.love_engine_proxy.skills.sandbox_executor import SkillsSandboxExecutor
from love_engine.llms.love_engine_proxy.skills.transformation import (
    LoveEngineSkillsTransformationHandler,
)

__all__ = [
    "LoveEngineSkillsHandler",
    "LoveEngineSkillsTransformationHandler",
    "SkillPromptInjectionHandler",
    "SkillsSandboxExecutor",
    "CodeExecutionHandler",
    "LoveEngineInternalTools",
    "LOVE_ENGINE_CODE_EXECUTION_TOOL",
    "get_love_engine_code_execution_tool",
    "code_execution_handler",
    "has_code_execution_tool",
    "add_code_execution_tool",
    "DEFAULT_MAX_ITERATIONS",
    "DEFAULT_SANDBOX_TIMEOUT",
]
