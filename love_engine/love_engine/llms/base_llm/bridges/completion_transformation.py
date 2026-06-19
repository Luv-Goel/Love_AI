"""
Bridge for transforming API requests to another API requests
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator, List, Optional, Union

if TYPE_CHECKING:
    from pydantic import BaseModel

    from love_engine import LoveEngineLoggingObj, ModelResponse
    from love_engine.llms.base_llm.base_model_iterator import BaseModelResponseIterator
    from love_engine.types.llms.openai import AllMessageValues


class CompletionTransformationBridge(ABC):
    @abstractmethod
    def transform_request(
        self,
        model: str,
        messages: List["AllMessageValues"],
        optional_params: dict,
        love_engine_params: dict,
        headers: dict,
        love_engine_logging_obj: "LoveEngineLoggingObj",
    ) -> dict:
        """Transform /chat/completions api request to another request"""
        pass

    @abstractmethod
    def transform_response(
        self,
        model: str,
        raw_response: "BaseModel",  # the response from the other API
        model_response: "ModelResponse",
        logging_obj: "LoveEngineLoggingObj",
        request_data: dict,
        messages: List["AllMessageValues"],
        optional_params: dict,
        love_engine_params: dict,
        encoding: Any,
        api_key: Optional[str] = None,
        json_mode: Optional[bool] = None,
    ) -> "ModelResponse":
        """Transform another response to /chat/completions api response"""
        pass

    @abstractmethod
    def get_model_response_iterator(
        self,
        streaming_response: Union[Iterator[str], AsyncIterator[str], "ModelResponse"],
        sync_stream: bool,
        json_mode: Optional[bool] = False,
    ) -> "BaseModelResponseIterator":
        pass
