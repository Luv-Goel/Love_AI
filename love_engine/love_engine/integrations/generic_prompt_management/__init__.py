"""Generic prompt management integration for love_engine."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .generic_prompt_manager import GenericPromptManager
    from love_engine.types.prompts.init_prompts import PromptLoveEngineParams, PromptSpec
    from love_engine.integrations.custom_prompt_management import CustomPromptManagement

from love_engine.types.prompts.init_prompts import SupportedPromptIntegrations

from .generic_prompt_manager import GenericPromptManager

# Global instances
global_generic_prompt_config: Optional[dict] = None


def set_global_generic_prompt_config(config: dict) -> None:
    """
    Set the global generic prompt configuration.

    Args:
        config: Dictionary containing generic prompt configuration
                - api_base: Base URL for the API
                - api_key: Optional API key for authentication
                - timeout: Request timeout in seconds (default: 30)
    """
    import love_engine

    love_engine.global_generic_prompt_config = config  # type: ignore


def prompt_initializer(
    love_engine_params: "PromptLoveEngineParams", prompt_spec: "PromptSpec"
) -> "CustomPromptManagement":
    """
    Initialize a prompt from a generic prompt management API.
    """
    prompt_id = getattr(love_engine_params, "prompt_id", None)

    api_base = love_engine_params.api_base
    api_key = love_engine_params.api_key
    if not api_base:
        raise ValueError("api_base is required in generic_prompt_config")

    provider_specific_query_params = love_engine_params.provider_specific_query_params

    try:
        generic_prompt_manager = GenericPromptManager(
            api_base=api_base,
            api_key=api_key,
            prompt_id=prompt_id,
            additional_provider_specific_query_params=provider_specific_query_params,
            **love_engine_params.model_dump(
                exclude_none=True,
                exclude={
                    "prompt_id",
                    "api_key",
                    "provider_specific_query_params",
                    "api_base",
                },
            ),
        )

        return generic_prompt_manager
    except Exception as e:
        raise e


prompt_initializer_registry = {
    SupportedPromptIntegrations.GENERIC_PROMPT_MANAGEMENT.value: prompt_initializer,
}

# Export public API
__all__ = [
    "GenericPromptManager",
    "set_global_generic_prompt_config",
    "global_generic_prompt_config",
    "prompt_initializer_registry",
]
