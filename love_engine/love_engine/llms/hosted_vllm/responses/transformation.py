"""
Responses API transformation for Hosted VLLM provider.

vLLM natively supports the OpenAI-compatible /v1/responses endpoint,
so this config enables direct routing instead of falling back to
the chat completions → responses conversion pipeline.
"""

from typing import Optional

from love_engine.llms.openai.responses.transformation import OpenAIResponsesAPIConfig
from love_engine.secret_managers.main import get_secret_str
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import LlmProviders


class HostedVLLMResponsesAPIConfig(OpenAIResponsesAPIConfig):
    """
    Configuration for Hosted VLLM Responses API support.

    Extends OpenAI's config since vLLM follows OpenAI's API spec,
    but uses HOSTED_VLLM_API_BASE for the base URL and defaults
    to "fake-api-key" when no API key is provided (vLLM does not
    require authentication by default).
    """

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.HOSTED_VLLM

    def validate_environment(
        self,
        headers: dict,
        model: str,
        love_engine_params: Optional[GenericLoveEngineParams],
    ) -> dict:
        love_engine_params = love_engine_params or GenericLoveEngineParams()
        api_key = (
            love_engine_params.api_key
            or get_secret_str("HOSTED_VLLM_API_KEY")
            or "fake-api-key"
        )  # vllm does not require an api key
        headers.update(
            {
                "Authorization": f"Bearer {api_key}",
            }
        )
        return headers

    def get_complete_url(
        self,
        api_base: Optional[str],
        love_engine_params: dict,
    ) -> str:
        api_base = api_base or get_secret_str("HOSTED_VLLM_API_BASE")

        if api_base is None:
            raise ValueError(
                "api_base not set for Hosted VLLM responses API. "
                "Set via api_base parameter or HOSTED_VLLM_API_BASE environment variable"
            )

        # Remove trailing slashes
        api_base = api_base.rstrip("/")

        # If api_base already ends with /v1, append /responses
        # Otherwise append /v1/responses
        if api_base.endswith("/v1"):
            return f"{api_base}/responses"

        return f"{api_base}/v1/responses"

    def supports_native_websocket(self) -> bool:
        """Hosted vLLM does not support native WebSocket for Responses API"""
        return False
