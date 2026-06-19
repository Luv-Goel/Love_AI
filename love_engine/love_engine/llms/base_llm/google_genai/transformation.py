import types
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import httpx

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
    from love_engine.types.google_genai.main import (
        GenerateContentConfigDict,
        GenerateContentContentListUnionDict,
        GenerateContentResponse,
        ToolConfigDict,
    )
else:
    GenerateContentConfigDict = Any
    GenerateContentContentListUnionDict = Any
    GenerateContentResponse = Any
    LoveEngineLoggingObj = Any
    ToolConfigDict = Any

from love_engine.types.router import GenericLoveEngineParams


class BaseGoogleGenAIGenerateContentConfig(ABC):
    """Base configuration class for Google GenAI generate_content functionality"""

    def __init__(self):
        pass

    @classmethod
    def get_config(cls):
        return {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("__")
            and not k.startswith("_abc")
            and not isinstance(
                v,
                (
                    types.FunctionType,
                    types.BuiltinFunctionType,
                    classmethod,
                    staticmethod,
                ),
            )
            and v is not None
        }

    @abstractmethod
    def get_supported_generate_content_optional_params(self, model: str) -> List[str]:
        """
        Get the list of supported Google GenAI parameters for the model.

        Args:
            model: The model name

        Returns:
            List of supported parameter names
        """
        raise NotImplementedError(
            "get_supported_generate_content_optional_params is not implemented"
        )

    @abstractmethod
    def map_generate_content_optional_params(
        self,
        generate_content_config_dict: GenerateContentConfigDict,
        model: str,
    ) -> Dict[str, Any]:
        """
        Map Google GenAI parameters to provider-specific format.

        Args:
            generate_content_optional_params: Optional parameters for generate content
            model: The model name

        Returns:
            Mapped parameters for the provider
        """
        raise NotImplementedError(
            "map_generate_content_optional_params is not implemented"
        )

    @abstractmethod
    def validate_environment(
        self,
        api_key: Optional[str],
        headers: Optional[dict],
        model: str,
        love_engine_params: Optional[Union[GenericLoveEngineParams, dict]],
    ) -> dict:
        """
        Validate the environment and return headers for the request.

        Args:
            api_key: API key
            headers: Existing headers
            model: The model name
            love_engine_params: love_engine parameters

        Returns:
            Updated headers
        """
        raise NotImplementedError("validate_environment is not implemented")

    def sync_get_auth_token_and_url(
        self,
        api_base: Optional[str],
        model: str,
        love_engine_params: dict,
        stream: bool,
    ) -> Tuple[dict, str]:
        """
        Sync version of get_auth_token_and_url.

        Args:
            api_base: Base API URL
            model: The model name
            love_engine_params: love_engine parameters
            stream: Whether this is a streaming call

        Returns:
            Tuple of headers and API base
        """
        raise NotImplementedError("sync_get_auth_token_and_url is not implemented")

    async def get_auth_token_and_url(
        self,
        api_base: Optional[str],
        model: str,
        love_engine_params: dict,
        stream: bool,
    ) -> Tuple[dict, str]:
        """
        Get the complete URL for the request.

        Args:
            api_base: Base API URL
            model: The model name
            love_engine_params: love_engine parameters

        Returns:
            Tuple of headers and API base
        """
        raise NotImplementedError("get_auth_token_and_url is not implemented")

    @abstractmethod
    def transform_generate_content_request(
        self,
        model: str,
        contents: GenerateContentContentListUnionDict,
        tools: Optional[ToolConfigDict],
        generate_content_config_dict: Dict,
        system_instruction: Optional[Any] = None,
    ) -> dict:
        """
        Transform the request parameters for the generate content API.

        Args:
            model: The model name
            contents: Input contents
            tools: Tools
            generate_content_config_dict: Generation config parameters
            system_instruction: Optional system instruction

        Returns:
            Transformed request data
        """
        pass

    @abstractmethod
    def transform_generate_content_response(
        self,
        model: str,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> GenerateContentResponse:
        """
        Transform the raw response from the generate content API.

        Args:
            model: The model name
            raw_response: Raw HTTP response

        Returns:
            Transformed response data
        """
        pass

    def get_error_class(
        self, error_message: str, status_code: int, headers: Union[dict, httpx.Headers]
    ) -> Exception:
        """
        Get the appropriate exception class for the error.

        Args:
            error_message: Error message
            status_code: HTTP status code
            headers: Response headers

        Returns:
            Exception instance
        """
        from love_engine.llms.base_llm.chat.transformation import BaseLLMException

        return BaseLLMException(
            status_code=status_code,
            message=error_message,
            headers=headers,
        )
