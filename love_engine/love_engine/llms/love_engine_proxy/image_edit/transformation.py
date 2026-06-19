from typing import Optional

from love_engine.llms.openai.image_edit.transformation import OpenAIImageEditConfig
from love_engine.secret_managers.main import get_secret_str


class LoveEngineProxyImageEditConfig(OpenAIImageEditConfig):
    """Configuration for image edit requests routed through love_engine Proxy."""

    def validate_environment(
        self,
        headers: dict,
        model: str,
        api_key: Optional[str] = None,
        love_engine_params: Optional[dict] = None,
        api_base: Optional[str] = None,
    ) -> dict:
        api_key = api_key or get_secret_str("LOVE_ENGINE_PROXY_API_KEY")
        headers.update({"Authorization": f"Bearer {api_key}"})
        return headers

    def get_complete_url(
        self, model: str, api_base: Optional[str], love_engine_params: dict
    ) -> str:
        api_base = api_base or get_secret_str("LOVE_ENGINE_PROXY_API_BASE")
        if api_base is None:
            raise ValueError(
                "api_base not set for love_engine Proxy route. Set in env via `LOVE_ENGINE_PROXY_API_BASE`"
            )
        api_base = api_base.rstrip("/")
        return f"{api_base}/images/edits"
