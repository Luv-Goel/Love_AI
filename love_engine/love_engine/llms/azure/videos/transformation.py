from typing import TYPE_CHECKING, Any, Dict, Optional

from love_engine.types.videos.main import VideoCreateOptionalRequestParams
from love_engine.types.router import GenericLoveEngineParams
from love_engine.llms.azure.common_utils import BaseAzureLLM
from love_engine.llms.openai.videos.transformation import OpenAIVideoConfig

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as _LoveEngineLoggingObj

    from ...base_llm.videos.transformation import BaseVideoConfig as _BaseVideoConfig
    from ...base_llm.chat.transformation import BaseLLMException as _BaseLLMException

    LoveEngineLoggingObj = _LoveEngineLoggingObj
    BaseVideoConfig = _BaseVideoConfig
    BaseLLMException = _BaseLLMException
else:
    LoveEngineLoggingObj = Any
    BaseVideoConfig = Any
    BaseLLMException = Any


class AzureVideoConfig(OpenAIVideoConfig):
    """
    Configuration class for OpenAI video generation.
    """

    def __init__(self):
        super().__init__()

    def get_supported_openai_params(self, model: str) -> list:
        """
        Get the list of supported OpenAI parameters for video generation.
        """
        return [
            "model",
            "prompt",
            "input_reference",
            "seconds",
            "size",
            "user",
            "extra_headers",
        ]

    def map_openai_params(
        self,
        video_create_optional_params: VideoCreateOptionalRequestParams,
        model: str,
        drop_params: bool,
    ) -> Dict:
        """No mapping applied since inputs are in OpenAI spec already"""
        return dict(video_create_optional_params)

    def validate_environment(
        self,
        headers: dict,
        model: str,
        api_key: Optional[str] = None,
        love_engine_params: Optional[GenericLoveEngineParams] = None,
    ) -> dict:
        """
        Validate Azure environment and set up authentication headers.
        Uses _base_validate_azure_environment to properly handle credentials from love_engine_credential_name.
        """
        # If love_engine_params is provided, use it; otherwise create a new one
        if love_engine_params is None:
            love_engine_params = GenericLoveEngineParams()

        if api_key and not love_engine_params.api_key:
            love_engine_params.api_key = api_key

        # Use the base Azure validation method which properly handles:
        # 1. Credentials from love_engine_credential_name via love_engine_params
        # 2. Sets the correct "api-key" header (not "Authorization: Bearer")
        return BaseAzureLLM._base_validate_azure_environment(
            headers=headers, love_engine_params=love_engine_params
        )

    def get_complete_url(
        self,
        model: str,
        api_base: Optional[str],
        love_engine_params: dict,
    ) -> str:
        """
        Constructs a complete URL for the API request.
        """
        return BaseAzureLLM._get_base_azure_url(
            api_base=api_base,
            love_engine_params=love_engine_params,
            route="/openai/v1/videos",
            default_api_version="",
        )
