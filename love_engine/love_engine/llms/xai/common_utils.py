from typing import List, Optional

import httpx

import love_engine
from love_engine.llms.base_llm.base_utils import BaseLLMModelInfo
from love_engine.secret_managers.main import get_secret_str
from love_engine.types.llms.openai import AllMessageValues
from love_engine.types.utils import ProviderSpecificModelInfo


class XAIModelInfo(BaseLLMModelInfo):
    def get_provider_info(
        self,
        model: str,
    ) -> Optional[ProviderSpecificModelInfo]:
        """
        Default values all models of this provider support.
        """
        return {
            "supports_web_search": True,
        }

    def validate_environment(
        self,
        headers: dict,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> dict:
        if api_key is not None:
            headers["Authorization"] = f"Bearer {api_key}"

        # Ensure Content-Type is set to application/json
        if "content-type" not in headers and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        return headers

    @staticmethod
    def get_api_base(api_base: Optional[str] = None) -> Optional[str]:
        return api_base or get_secret_str("XAI_API_BASE") or "https://api.x.ai"

    @staticmethod
    def get_api_key(
        api_key: Optional[str] = None,
        legacy_generic_before_env: bool = False,
    ) -> Optional[str]:
        """
        Resolve xAI API keys while preserving endpoint-specific legacy order.

        Chat uses xai_key before XAI_API_KEY without adding a generic
        love_engine.api_key fallback. Responses and realtime historically
        preferred love_engine.api_key over XAI_API_KEY, so those paths opt into
        the legacy order with legacy_generic_before_env=True. In both modes,
        the provider-specific love_engine.xai_key takes precedence over fallbacks.
        """
        if legacy_generic_before_env:
            return (
                api_key
                or love_engine.xai_key
                or love_engine.api_key
                or get_secret_str("XAI_API_KEY")
            )

        return api_key or love_engine.xai_key or get_secret_str("XAI_API_KEY")

    @staticmethod
    def get_base_model(model: str) -> Optional[str]:
        return model.replace("xai/", "")

    def get_models(
        self, api_key: Optional[str] = None, api_base: Optional[str] = None
    ) -> List[str]:
        api_base = self.get_api_base(api_base)
        api_key = self.get_api_key(api_key)
        if api_base is None or api_key is None:
            raise ValueError(
                "XAI API base or key is not set. Set XAI_API_BASE and provide an xAI API key via api_key, love_engine.xai_key, or XAI_API_KEY."
            )
        response = love_engine.module_level_client.get(
            url=f"{api_base}/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise Exception(
                f"Failed to fetch models from XAI. Status code: {response.status_code}, Response: {response.text}"
            )

        models = response.json()["data"]

        love_engine_model_names = []
        for model in models:
            stripped_model_name = model["id"]
            love_engine_model_name = "xai/" + stripped_model_name
            love_engine_model_names.append(love_engine_model_name)
        return love_engine_model_names
