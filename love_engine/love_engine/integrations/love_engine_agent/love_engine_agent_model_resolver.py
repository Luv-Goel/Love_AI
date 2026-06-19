"""
Hook for love_engine that strips the love_engine_agent/ prefix from model names.

When model is love_engine_agent/gpt-3.5-turbo, this hook replaces it with gpt-3.5-turbo
before the completion call, similar to langfuse/model resolution.
"""

from typing import Dict, List, Optional, Tuple

from love_engine.integrations.custom_logger import CustomLogger
from love_engine.types.llms.openai import AllMessageValues
from love_engine.types.prompts.init_prompts import PromptSpec
from love_engine.types.utils import StandardCallbackDynamicParams

LOVE_ENGINE_AGENT_PREFIX = "love_engine_agent/"


class LoveEngineAgentModelResolver(CustomLogger):
    """
    CustomLogger that strips love_engine_agent/ prefix from model names.

    Enables model configs like love_engine_agent/gpt-3.5-turbo to resolve to gpt-3.5-turbo.
    """

    def get_chat_completion_prompt(
        self,
        model: str,
        messages: List[AllMessageValues],
        non_default_params: dict,
        prompt_id: Optional[str],
        prompt_variables: Optional[dict],
        dynamic_callback_params: StandardCallbackDynamicParams,
        prompt_spec: Optional[PromptSpec] = None,
        prompt_label: Optional[str] = None,
        prompt_version: Optional[int] = None,
        ignore_prompt_manager_model: Optional[bool] = False,
        ignore_prompt_manager_optional_params: Optional[bool] = False,
    ) -> Tuple[str, List[AllMessageValues], dict]:
        """
        Strip love_engine_agent/ prefix from model name.

        Returns:
            (resolved_model, messages, non_default_params)
        """
        if ignore_prompt_manager_model:
            return model, messages, non_default_params
        resolved_model = model.replace(LOVE_ENGINE_AGENT_PREFIX, "", 1)
        return resolved_model, messages, non_default_params

    async def async_get_chat_completion_prompt(
        self,
        model: str,
        messages: List[AllMessageValues],
        non_default_params: dict,
        prompt_id: Optional[str],
        prompt_variables: Optional[dict],
        dynamic_callback_params: StandardCallbackDynamicParams,
        love_engine_logging_obj: object,
        prompt_spec: Optional[PromptSpec] = None,
        tools: Optional[List[Dict]] = None,
        prompt_label: Optional[str] = None,
        prompt_version: Optional[int] = None,
        ignore_prompt_manager_model: Optional[bool] = False,
        ignore_prompt_manager_optional_params: Optional[bool] = False,
    ) -> Tuple[str, List[AllMessageValues], dict]:
        """Async delegate to get_chat_completion_prompt."""
        return self.get_chat_completion_prompt(
            model=model,
            messages=messages,
            non_default_params=non_default_params,
            prompt_id=prompt_id,
            prompt_variables=prompt_variables,
            dynamic_callback_params=dynamic_callback_params,
            prompt_spec=prompt_spec,
            prompt_label=prompt_label,
            prompt_version=prompt_version,
            ignore_prompt_manager_model=ignore_prompt_manager_model,
            ignore_prompt_manager_optional_params=ignore_prompt_manager_optional_params,
        )
