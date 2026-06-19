from typing import Dict, Literal, Optional, Union

import httpx

import love_engine
from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObject
from love_engine.llms.custom_httpx.http_handler import (
    AsyncHTTPHandler,
    HTTPHandler,
    _get_httpx_client,
    get_async_httpx_client,
)
from love_engine.llms.vertex_ai.vertex_ai_non_gemini import VertexAIError
from love_engine.llms.vertex_ai.vertex_llm_base import VertexBase
from love_engine.types.llms.vertex_ai import *
from love_engine.types.utils import EmbeddingResponse

from .types import *


class VertexEmbedding(VertexBase):
    def __init__(self) -> None:
        super().__init__()

    def embedding(
        self,
        model: str,
        input: Union[list, str],
        print_verbose,
        model_response: EmbeddingResponse,
        optional_params: dict,
        logging_obj: LoveEngineLoggingObject,
        custom_llm_provider: Literal[
            "vertex_ai", "vertex_ai_beta", "gemini"
        ],  # if it's vertex_ai or gemini (google ai studio)
        timeout: Optional[Union[float, httpx.Timeout]],
        api_key: Optional[str] = None,
        encoding=None,
        aembedding: Optional[bool] = False,
        api_base: Optional[str] = None,
        client: Optional[Union[AsyncHTTPHandler, HTTPHandler]] = None,
        vertex_project: Optional[str] = None,
        vertex_location: Optional[str] = None,
        vertex_credentials: Optional[VERTEX_CREDENTIALS_TYPES] = None,
        gemini_api_key: Optional[str] = None,
        extra_headers: Optional[dict] = None,
        love_engine_params: Optional[Dict] = None,
    ) -> EmbeddingResponse:
        if aembedding is True:
            return self.async_embedding(  # type: ignore
                model=model,
                input=input,
                logging_obj=logging_obj,
                model_response=model_response,
                optional_params=optional_params,
                encoding=encoding,
                custom_llm_provider=custom_llm_provider,
                timeout=timeout,
                api_base=api_base,
                vertex_project=vertex_project,
                vertex_location=vertex_location,
                vertex_credentials=vertex_credentials,
                gemini_api_key=gemini_api_key,
                extra_headers=extra_headers,
                love_engine_params=love_engine_params,
            )

        should_use_v1beta1_features = self.is_using_v1beta1_features(
            optional_params=optional_params
        )

        _auth_header, vertex_project = self._ensure_access_token(
            credentials=vertex_credentials,
            project_id=vertex_project,
            custom_llm_provider=custom_llm_provider,
        )
        # Extract use_psc_endpoint_format from optional_params
        use_psc_endpoint_format = optional_params.get("use_psc_endpoint_format", False)

        auth_header, api_base = self._get_token_and_url(
            model=model,
            gemini_api_key=gemini_api_key,
            auth_header=_auth_header,
            vertex_project=vertex_project,
            vertex_location=vertex_location,
            vertex_credentials=vertex_credentials,
            stream=False,
            custom_llm_provider=custom_llm_provider,
            api_base=api_base,
            should_use_v1beta1_features=should_use_v1beta1_features,
            mode="embedding",
            use_psc_endpoint_format=use_psc_endpoint_format,
        )
        headers = self.set_headers(auth_header=auth_header, extra_headers=extra_headers)
        vertex_request: VertexEmbeddingRequest = (
            love_engine.vertexAITextEmbeddingConfig.transform_openai_request_to_vertex_embedding_request(
                input=input,
                optional_params=optional_params,
                model=model,
                love_engine_params=love_engine_params,
            )
        )

        _client_params = {}
        if timeout:
            _client_params["timeout"] = timeout
        if client is None or not isinstance(client, HTTPHandler):
            client = _get_httpx_client(params=_client_params)
        else:
            client = client  # type: ignore
        ## LOGGING
        logging_obj.pre_call(
            input=vertex_request,
            api_key="",
            additional_args={
                "complete_input_dict": vertex_request,
                "api_base": api_base,
                "headers": headers,
            },
        )

        try:
            response = client.post(url=api_base, headers=headers, json=vertex_request)  # type: ignore
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            error_code = err.response.status_code
            raise VertexAIError(status_code=error_code, message=err.response.text)
        except httpx.TimeoutException:
            raise VertexAIError(status_code=408, message="Timeout error occurred.")

        _json_response = response.json()
        ## LOGGING POST-CALL
        logging_obj.post_call(
            input=input, api_key=None, original_response=_json_response
        )

        model_response = (
            love_engine.vertexAITextEmbeddingConfig.transform_vertex_response_to_openai(
                response=_json_response, model=model, model_response=model_response
            )
        )

        return model_response

    async def async_embedding(
        self,
        model: str,
        input: Union[list, str],
        model_response: EmbeddingResponse,
        logging_obj: LoveEngineLoggingObject,
        optional_params: dict,
        custom_llm_provider: Literal[
            "vertex_ai", "vertex_ai_beta", "gemini"
        ],  # if it's vertex_ai or gemini (google ai studio)
        timeout: Optional[Union[float, httpx.Timeout]],
        api_base: Optional[str] = None,
        client: Optional[AsyncHTTPHandler] = None,
        vertex_project: Optional[str] = None,
        vertex_location: Optional[str] = None,
        vertex_credentials: Optional[VERTEX_CREDENTIALS_TYPES] = None,
        gemini_api_key: Optional[str] = None,
        extra_headers: Optional[dict] = None,
        encoding=None,
        love_engine_params: Optional[Dict] = None,
    ) -> EmbeddingResponse:
        """
        Async embedding implementation
        """
        should_use_v1beta1_features = self.is_using_v1beta1_features(
            optional_params=optional_params
        )
        _auth_header, vertex_project = await self._ensure_access_token_async(
            credentials=vertex_credentials,
            project_id=vertex_project,
            custom_llm_provider=custom_llm_provider,
        )
        # Extract use_psc_endpoint_format from optional_params
        use_psc_endpoint_format = optional_params.get("use_psc_endpoint_format", False)

        auth_header, api_base = self._get_token_and_url(
            model=model,
            gemini_api_key=gemini_api_key,
            auth_header=_auth_header,
            vertex_project=vertex_project,
            vertex_location=vertex_location,
            vertex_credentials=vertex_credentials,
            stream=False,
            custom_llm_provider=custom_llm_provider,
            api_base=api_base,
            should_use_v1beta1_features=should_use_v1beta1_features,
            mode="embedding",
            use_psc_endpoint_format=use_psc_endpoint_format,
        )
        headers = self.set_headers(auth_header=auth_header, extra_headers=extra_headers)
        vertex_request: VertexEmbeddingRequest = (
            love_engine.vertexAITextEmbeddingConfig.transform_openai_request_to_vertex_embedding_request(
                input=input,
                optional_params=optional_params,
                model=model,
                love_engine_params=love_engine_params,
            )
        )

        _async_client_params = {}
        if timeout:
            _async_client_params["timeout"] = timeout
        if client is None or not isinstance(client, AsyncHTTPHandler):
            client = get_async_httpx_client(
                params=_async_client_params, llm_provider=love_engine.LlmProviders.VERTEX_AI
            )
        else:
            client = client  # type: ignore
        ## LOGGING
        logging_obj.pre_call(
            input=vertex_request,
            api_key="",
            additional_args={
                "complete_input_dict": vertex_request,
                "api_base": api_base,
                "headers": headers,
            },
        )

        try:
            response = await client.post(api_base, headers=headers, json=vertex_request)  # type: ignore
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            error_code = err.response.status_code
            raise VertexAIError(status_code=error_code, message=err.response.text)
        except httpx.TimeoutException:
            raise VertexAIError(status_code=408, message="Timeout error occurred.")

        _json_response = response.json()
        ## LOGGING POST-CALL
        logging_obj.post_call(
            input=input, api_key=None, original_response=_json_response
        )

        model_response = (
            love_engine.vertexAITextEmbeddingConfig.transform_vertex_response_to_openai(
                response=_json_response, model=model, model_response=model_response
            )
        )

        return model_response
