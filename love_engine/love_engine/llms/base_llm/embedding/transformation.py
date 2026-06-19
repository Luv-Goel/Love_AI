from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, Optional

import httpx

from love_engine.llms.base_llm.chat.transformation import BaseConfig
from love_engine.types.llms.openai import AllEmbeddingInputValues, AllMessageValues
from love_engine.types.utils import EmbeddingResponse, ModelResponse

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as _LoveEngineLoggingObj

    LoveEngineLoggingObj = _LoveEngineLoggingObj
else:
    LoveEngineLoggingObj = Any


class BaseEmbeddingConfig(BaseConfig, ABC):
    @abstractmethod
    def transform_embedding_request(
        self,
        model: str,
        input: AllEmbeddingInputValues,
        optional_params: dict,
        headers: dict,
    ) -> dict:
        return {}

    @abstractmethod
    def transform_embedding_response(
        self,
        model: str,
        raw_response: httpx.Response,
        model_response: EmbeddingResponse,
        logging_obj: LoveEngineLoggingObj,
        api_key: Optional[str],
        request_data: dict,
        optional_params: dict,
        love_engine_params: dict,
    ) -> EmbeddingResponse:
        return model_response

    def get_complete_url(
        self,
        api_base: Optional[str],
        api_key: Optional[str],
        model: str,
        optional_params: dict,
        love_engine_params: dict,
        stream: Optional[bool] = None,
    ) -> str:
        """
        OPTIONAL

        Get the complete url for the request

        Some providers need `model` in `api_base`
        """
        return api_base or ""

    def transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        headers: dict,
    ) -> dict:
        raise NotImplementedError(
            "EmbeddingConfig does not need a request transformation for chat models"
        )

    def transform_response(
        self,
        model: str,
        raw_response: httpx.Response,
        model_response: ModelResponse,
        logging_obj: LoveEngineLoggingObj,
        request_data: dict,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        encoding: Any,
        api_key: Optional[str] = None,
        json_mode: Optional[bool] = None,
    ) -> ModelResponse:
        raise NotImplementedError(
            "EmbeddingConfig does not need a response transformation for chat models"
        )
