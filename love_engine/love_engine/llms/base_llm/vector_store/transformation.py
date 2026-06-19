from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import httpx

from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.vector_stores import (
    VECTOR_STORE_OPENAI_PARAMS,
    BaseVectorStoreAuthCredentials,
    VectorStoreCreateOptionalRequestParams,
    VectorStoreCreateResponse,
    VectorStoreIndexEndpoints,
    VectorStoreSearchOptionalRequestParams,
    VectorStoreSearchResponse,
)

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as _LoveEngineLoggingObj

    from ..chat.transformation import BaseLLMException as _BaseLLMException

    LoveEngineLoggingObj = _LoveEngineLoggingObj
    BaseLLMException = _BaseLLMException
else:
    LoveEngineLoggingObj = Any
    BaseLLMException = Any


class BaseVectorStoreConfig:
    def get_supported_openai_params(
        self, model: str
    ) -> List[VECTOR_STORE_OPENAI_PARAMS]:
        return []

    def map_openai_params(
        self,
        non_default_params: dict,
        optional_params: dict,
        drop_params: bool,
    ) -> dict:
        return optional_params

    @abstractmethod
    def get_auth_credentials(
        self, love_engine_params: dict
    ) -> BaseVectorStoreAuthCredentials:
        pass

    @abstractmethod
    def get_vector_store_endpoints_by_type(self) -> VectorStoreIndexEndpoints:
        pass

    @abstractmethod
    def transform_search_vector_store_request(
        self,
        vector_store_id: str,
        query: Union[str, List[str]],
        vector_store_search_optional_params: VectorStoreSearchOptionalRequestParams,
        api_base: str,
        love_engine_logging_obj: LoveEngineLoggingObj,
        love_engine_params: dict,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict]:
        pass

    async def atransform_search_vector_store_request(
        self,
        vector_store_id: str,
        query: Union[str, List[str]],
        vector_store_search_optional_params: VectorStoreSearchOptionalRequestParams,
        api_base: str,
        love_engine_logging_obj: LoveEngineLoggingObj,
        love_engine_params: dict,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict]:
        """
        Optional async version of transform_search_vector_store_request.
        If not implemented, the handler will fall back to the sync version.
        Providers that need to make async calls (e.g., generating embeddings) should override this.
        """
        # Default implementation: call the sync version
        return self.transform_search_vector_store_request(
            vector_store_id=vector_store_id,
            query=query,
            vector_store_search_optional_params=vector_store_search_optional_params,
            api_base=api_base,
            love_engine_logging_obj=love_engine_logging_obj,
            love_engine_params=love_engine_params,
            extra_body=extra_body,
        )

    @abstractmethod
    def transform_search_vector_store_response(
        self, response: httpx.Response, love_engine_logging_obj: LoveEngineLoggingObj
    ) -> VectorStoreSearchResponse:
        pass

    @abstractmethod
    def transform_create_vector_store_request(
        self,
        vector_store_create_optional_params: VectorStoreCreateOptionalRequestParams,
        api_base: str,
    ) -> Tuple[str, Dict]:
        pass

    @abstractmethod
    def transform_create_vector_store_response(
        self, response: httpx.Response
    ) -> VectorStoreCreateResponse:
        pass

    @abstractmethod
    def validate_environment(
        self, headers: dict, love_engine_params: Optional[GenericLoveEngineParams]
    ) -> dict:
        return {}

    @abstractmethod
    def get_complete_url(
        self,
        api_base: Optional[str],
        love_engine_params: dict,
    ) -> str:
        """
        OPTIONAL

        Get the complete url for the request

        Some providers need `model` in `api_base`
        """
        if api_base is None:
            raise ValueError("api_base is required")
        return api_base

    def get_error_class(
        self, error_message: str, status_code: int, headers: Union[dict, httpx.Headers]
    ) -> BaseLLMException:
        from ..chat.transformation import BaseLLMException

        raise BaseLLMException(
            status_code=status_code,
            message=error_message,
            headers=headers,
        )

    def sign_request(
        self,
        headers: dict,
        optional_params: Dict,
        request_data: Dict,
        api_base: str,
        api_key: Optional[str] = None,
    ) -> Tuple[dict, Optional[bytes]]:
        """Optionally sign or modify the request before sending.

        Providers like AWS Bedrock require SigV4 signing. Providers that don't
        require any signing can simply return the headers unchanged and ``None``
        for the signed body.
        """
        return headers, None

    def calculate_vector_store_cost(
        self,
        response: VectorStoreSearchResponse,
    ) -> Tuple[float, float]:
        return 0.0, 0.0
