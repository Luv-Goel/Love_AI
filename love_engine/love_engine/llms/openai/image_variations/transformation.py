from typing import Any, List, Optional, Union

from aiohttp import ClientResponse
from httpx import Headers, Response

from love_engine.llms.base_llm.chat.transformation import BaseLLMException
from love_engine.llms.base_llm.image_variations.transformation import LoveEngineLoggingObj
from love_engine.types.llms.openai import OpenAIImageVariationOptionalParams
from love_engine.types.utils import FileTypes, HttpHandlerRequestFields, ImageResponse

from ...base_llm.image_variations.transformation import BaseImageVariationConfig
from ..common_utils import OpenAIError


class OpenAIImageVariationConfig(BaseImageVariationConfig):
    def get_supported_openai_params(
        self, model: str
    ) -> List[OpenAIImageVariationOptionalParams]:
        return ["n", "size", "response_format", "user"]

    def map_openai_params(
        self,
        non_default_params: dict,
        optional_params: dict,
        model: str,
        drop_params: bool,
    ) -> dict:
        optional_params.update(non_default_params)
        return optional_params

    def transform_request_image_variation(
        self,
        model: Optional[str],
        image: FileTypes,
        optional_params: dict,
        headers: dict,
    ) -> HttpHandlerRequestFields:
        return {
            "data": {
                "image": image,
                **optional_params,
            }
        }

    async def async_transform_response_image_variation(
        self,
        model: Optional[str],
        raw_response: ClientResponse,
        model_response: ImageResponse,
        logging_obj: LoveEngineLoggingObj,
        request_data: dict,
        image: FileTypes,
        optional_params: dict,
        love_engine_params: dict,
        encoding: Any,
        api_key: Optional[str] = None,
    ) -> ImageResponse:
        return model_response

    def transform_response_image_variation(
        self,
        model: Optional[str],
        raw_response: Response,
        model_response: ImageResponse,
        logging_obj: LoveEngineLoggingObj,
        request_data: dict,
        image: FileTypes,
        optional_params: dict,
        love_engine_params: dict,
        encoding: Any,
        api_key: Optional[str] = None,
    ) -> ImageResponse:
        return model_response

    def get_error_class(
        self, error_message: str, status_code: int, headers: Union[dict, Headers]
    ) -> BaseLLMException:
        return OpenAIError(
            status_code=status_code,
            message=error_message,
            headers=headers,
        )
