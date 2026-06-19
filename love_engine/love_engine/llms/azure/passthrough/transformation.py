from typing import TYPE_CHECKING, List, Optional, Tuple

import httpx
from httpx import Response

from love_engine.love_engine_core_utils.love_engine_logging import Logging
from love_engine.llms.azure.common_utils import BaseAzureLLM
from love_engine.llms.base_llm.passthrough.transformation import BasePassthroughConfig
from love_engine.secret_managers.main import get_secret_str
from love_engine.types.llms.openai import AllMessageValues
from love_engine.types.router import GenericLoveEngineParams

if TYPE_CHECKING:
    from httpx import URL

    from love_engine.types.utils import CostResponseTypes


class AzurePassthroughConfig(BasePassthroughConfig):
    def is_streaming_request(self, endpoint: str, request_data: dict) -> bool:
        return "stream" in request_data

    def get_complete_url(
        self,
        api_base: Optional[str],
        api_key: Optional[str],
        model: str,
        endpoint: str,
        request_query_params: Optional[dict],
        love_engine_params: dict,
    ) -> Tuple["URL", str]:
        base_target_url = self.get_api_base(api_base)

        if base_target_url is None:
            raise Exception("Azure api base not found")

        love_engine_metadata = love_engine_params.get("love_engine_metadata") or {}
        model_group = love_engine_metadata.get("model_group")
        if model_group and model_group in endpoint:
            endpoint = endpoint.replace(model_group, model)

        complete_url = BaseAzureLLM._get_base_azure_url(
            api_base=base_target_url,
            love_engine_params=love_engine_params,
            route=endpoint,
            default_api_version=love_engine_params.get("api_version"),
        )
        return (
            httpx.URL(complete_url),
            base_target_url,
        )

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
        return BaseAzureLLM._base_validate_azure_environment(
            headers=headers,
            love_engine_params=GenericLoveEngineParams(
                **{**love_engine_params, "api_key": api_key}
            ),
        )

    @staticmethod
    def get_api_base(
        api_base: Optional[str] = None,
    ) -> Optional[str]:
        return api_base or get_secret_str("AZURE_API_BASE")

    @staticmethod
    def get_api_key(
        api_key: Optional[str] = None,
    ) -> Optional[str]:
        return api_key or get_secret_str("AZURE_API_KEY")

    @staticmethod
    def get_base_model(model: str) -> Optional[str]:
        return model

    def get_models(
        self, api_key: Optional[str] = None, api_base: Optional[str] = None
    ) -> List[str]:
        return super().get_models(api_key, api_base)

    def logging_non_streaming_response(
        self,
        model: str,
        custom_llm_provider: str,
        httpx_response: Response,
        request_data: dict,
        logging_obj: Logging,
        endpoint: str,
    ) -> Optional["CostResponseTypes"]:
        from love_engine import encoding
        from love_engine.llms.openai.chat.gpt_transformation import OpenAIGPTConfig
        from love_engine.types.utils import ModelResponse

        if "chat/completions" not in endpoint:
            return None

        openai_chat_config = OpenAIGPTConfig()

        love_engine_model_response: ModelResponse = openai_chat_config.transform_response(
            model=model,
            messages=[{"role": "user", "content": "no-message-pass-through-endpoint"}],
            raw_response=httpx_response,
            model_response=ModelResponse(),
            logging_obj=logging_obj,
            optional_params={},
            love_engine_params={},
            api_key="",
            request_data=request_data,
            encoding=encoding,
        )

        return love_engine_model_response
