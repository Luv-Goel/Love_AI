"""
Responses API transformation for love_engine Proxy provider.

love_engine Proxy supports the OpenAI Responses API natively when the underlying model supports it.
This config enables pass-through behavior to the proxy's /v1/responses endpoint.
"""

from typing import Optional

from love_engine.llms.openai.responses.transformation import OpenAIResponsesAPIConfig
from love_engine.secret_managers.main import get_secret_str
from love_engine.types.utils import LlmProviders


class LoveEngineProxyResponsesAPIConfig(OpenAIResponsesAPIConfig):
    """
    Configuration for love_engine Proxy Responses API support.

    Extends OpenAI's config since the proxy follows OpenAI's API spec,
    but uses LOVE_ENGINE_PROXY_API_BASE for the base URL.
    """

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.LOVE_ENGINE_PROXY

    def get_complete_url(
        self,
        api_base: Optional[str],
        love_engine_params: dict,
    ) -> str:
        """
        Get the endpoint for love_engine Proxy responses API.

        Uses LOVE_ENGINE_PROXY_API_BASE environment variable if api_base is not provided.
        """
        api_base = api_base or get_secret_str("LOVE_ENGINE_PROXY_API_BASE")

        if api_base is None:
            raise ValueError(
                "api_base not set for love_engine Proxy responses API. "
                "Set via api_base parameter or LOVE_ENGINE_PROXY_API_BASE environment variable"
            )

        # Remove trailing slashes
        api_base = api_base.rstrip("/")

        return f"{api_base}/responses"

    def supports_native_websocket(self) -> bool:
        """love_engine Proxy does not support native WebSocket for Responses API"""
        return False
