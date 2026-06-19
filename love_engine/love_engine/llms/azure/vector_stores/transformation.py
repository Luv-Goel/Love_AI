from typing import Optional

from love_engine.llms.azure.common_utils import BaseAzureLLM
from love_engine.llms.openai.vector_stores.transformation import OpenAIVectorStoreConfig
from love_engine.types.router import GenericLoveEngineParams


class AzureOpenAIVectorStoreConfig(OpenAIVectorStoreConfig):
    def get_complete_url(
        self,
        api_base: Optional[str],
        love_engine_params: dict,
    ) -> str:
        return BaseAzureLLM._get_base_azure_url(
            api_base=api_base,
            love_engine_params=love_engine_params,
            route="/openai/vector_stores",
        )

    def validate_environment(
        self, headers: dict, love_engine_params: Optional[GenericLoveEngineParams]
    ) -> dict:
        return BaseAzureLLM._base_validate_azure_environment(
            headers=headers, love_engine_params=love_engine_params
        )
