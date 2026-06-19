import os
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from love_engine.types.prompts.init_prompts import PromptLoveEngineParams, PromptSpec
    from love_engine.integrations.custom_prompt_management import CustomPromptManagement

from love_engine.types.prompts.init_prompts import SupportedPromptIntegrations

from .arize_phoenix_prompt_manager import ArizePhoenixPromptManager

# Global instances
global_arize_config: Optional[dict] = None


def prompt_initializer(
    love_engine_params: "PromptLoveEngineParams", prompt_spec: "PromptSpec"
) -> "CustomPromptManagement":
    """
    Initialize a prompt from Arize Phoenix.
    """
    api_key = getattr(love_engine_params, "api_key", None) or os.environ.get(
        "PHOENIX_API_KEY"
    )
    api_base = getattr(love_engine_params, "api_base", None)
    prompt_id = getattr(love_engine_params, "prompt_id", None)

    if not api_key or not api_base:
        raise ValueError(
            "api_key and api_base are required for Arize Phoenix prompt integration"
        )

    try:
        arize_prompt_manager = ArizePhoenixPromptManager(
            **{
                "api_key": api_key,
                "api_base": api_base,
                "prompt_id": prompt_id,
                **love_engine_params.model_dump(
                    exclude={"api_key", "api_base", "prompt_id"}
                ),
            },
        )

        return arize_prompt_manager
    except Exception as e:
        raise e


prompt_initializer_registry = {
    SupportedPromptIntegrations.ARIZE_PHOENIX.value: prompt_initializer,
}
