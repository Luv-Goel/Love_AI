"""
Databricks Responses API configuration.

Inherits from OpenAIResponsesAPIConfig since Databricks' Responses API
is compatible with OpenAI's for GPT models.

Reference: https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/api-reference
"""

import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from love_engine.llms.databricks.common_utils import DatabricksBase
from love_engine.llms.openai.responses.transformation import OpenAIResponsesAPIConfig
from love_engine.types.llms.openai import ResponseInputParam
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import LlmProviders

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as _LoveEngineLoggingObj

    LoveEngineLoggingObj = _LoveEngineLoggingObj
else:
    LoveEngineLoggingObj = Any


class DatabricksResponsesAPIConfig(DatabricksBase, OpenAIResponsesAPIConfig):
    """
    Configuration for Databricks Responses API.

    Inherits from OpenAIResponsesAPIConfig since Databricks' Responses API
    is largely compatible with OpenAI's for GPT models.

    Note: The Responses API on Databricks is only compatible with OpenAI GPT models.
    """

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.DATABRICKS

    def validate_environment(
        self,
        headers: dict,
        model: str,
        love_engine_params: Optional[GenericLoveEngineParams],
    ) -> dict:
        love_engine_params = love_engine_params or GenericLoveEngineParams()
        api_key = love_engine_params.api_key or os.getenv("DATABRICKS_API_KEY")
        api_base = love_engine_params.api_base or os.getenv("DATABRICKS_API_BASE")

        # Reuse Databricks auth logic (OAuth M2M, PAT, SDK fallback).
        # custom_endpoint=False allows SDK auth fallback; the appended
        # /chat/completions suffix is harmless since we discard api_base
        # here and build the URL separately in get_complete_url().
        _, headers = self.databricks_validate_environment(
            api_key=api_key,
            api_base=api_base,
            endpoint_type="chat_completions",
            custom_endpoint=False,
            headers=headers,
        )

        headers["Content-Type"] = "application/json"
        return headers

    def get_complete_url(
        self,
        api_base: Optional[str],
        love_engine_params: dict,
    ) -> str:
        api_base = api_base or os.getenv("DATABRICKS_API_BASE")
        api_base = self._get_api_base(api_base)
        api_base = api_base.rstrip("/")
        return f"{api_base}/responses"

    def transform_responses_api_request(
        self,
        model: str,
        input: Union[str, ResponseInputParam],
        response_api_optional_request_params: Dict,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Dict:
        """
        Transform request for Databricks Responses API.

        Strips the 'databricks/' prefix from model name if present,
        then delegates to OpenAI's transformation.
        """
        # Strip provider prefix if present (e.g., "databricks/databricks-gpt-5-nano" -> "databricks-gpt-5-nano")
        if model.startswith("databricks/"):
            model = model[len("databricks/") :]

        return super().transform_responses_api_request(
            model=model,
            input=input,
            response_api_optional_request_params=response_api_optional_request_params,
            love_engine_params=love_engine_params,
            headers=headers,
        )

    def supports_native_websocket(self) -> bool:
        """Databricks does not support native WebSocket for Responses API"""
        return False
