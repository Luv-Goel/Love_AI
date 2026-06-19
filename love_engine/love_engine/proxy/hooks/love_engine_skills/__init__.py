"""
LoveEngine Skills Hook - Proxy integration for skills

This module provides the CustomLogger hook for skills processing.
The actual skill logic is in love_engine/llms/love_engine_proxy/skills/.

Usage:
    from love_engine.proxy.hooks.love_engine_skills import SkillsInjectionHook

    # Register hook in proxy
    love_engine.callbacks.append(SkillsInjectionHook())
"""

# Re-export from the SDK location for convenience
from love_engine.llms.love_engine_proxy.skills import (
    LOVE_ENGINE_CODE_EXECUTION_TOOL,
    CodeExecutionHandler,
    LoveEngineInternalTools,
    SkillPromptInjectionHandler,
    SkillsSandboxExecutor,
    code_execution_handler,
    get_love_engine_code_execution_tool,
)
from love_engine.proxy.hooks.love_engine_skills.main import (
    SkillsInjectionHook,
    skills_injection_hook,
)

__all__ = [
    "SkillsInjectionHook",
    "skills_injection_hook",
    "CodeExecutionHandler",
    "LoveEngineInternalTools",
    "LOVE_ENGINE_CODE_EXECUTION_TOOL",
    "get_love_engine_code_execution_tool",
    "code_execution_handler",
    "SkillPromptInjectionHandler",
    "SkillsSandboxExecutor",
]
