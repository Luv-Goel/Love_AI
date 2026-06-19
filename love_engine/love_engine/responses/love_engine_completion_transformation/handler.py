"""
Handler for transforming responses api requests to love_engine.completion requests
"""

from typing import Any, Coroutine, Dict, Optional, Union

import love_engine
from love_engine.responses.love_engine_completion_transformation.streaming_iterator import (
    LoveEngineCompletionStreamingIterator,
)
from love_engine.responses.love_engine_completion_transformation.transformation import (
    LoveEngineCompletionResponsesConfig,
)
from love_engine.responses.streaming_iterator import BaseResponsesAPIStreamingIterator
from love_engine.types.llms.openai import (
    ResponseInputParam,
    ResponsesAPIOptionalRequestParams,
    ResponsesAPIResponse,
)
from love_engine.types.utils import ModelResponse


class LoveEngineCompletionTransformationHandler:
    def response_api_handler(
        self,
        model: str,
        input: Union[str, ResponseInputParam],
        responses_api_request: ResponsesAPIOptionalRequestParams,
        custom_llm_provider: Optional[str] = None,
        _is_async: bool = False,
        stream: Optional[bool] = None,
        extra_headers: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Union[
        ResponsesAPIResponse,
        BaseResponsesAPIStreamingIterator,
        Coroutine[
            Any, Any, Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]
        ],
    ]:
        love_engine_completion_request: dict = (
            LoveEngineCompletionResponsesConfig.transform_responses_api_request_to_chat_completion_request(
                model=model,
                input=input,
                responses_api_request=responses_api_request,
                custom_llm_provider=custom_llm_provider,
                stream=stream,
                extra_headers=extra_headers,
                **kwargs,
            )
        )

        if _is_async:
            return self.async_response_api_handler(
                love_engine_completion_request=love_engine_completion_request,
                request_input=input,
                responses_api_request=responses_api_request,
                **kwargs,
            )

        completion_args = {}
        completion_args.update(kwargs)
        completion_args.update(love_engine_completion_request)

        love_engine_completion_response: Union[
            ModelResponse, love_engine.CustomStreamWrapper
        ] = love_engine.completion(
            **completion_args,
        )

        if isinstance(love_engine_completion_response, ModelResponse):
            responses_api_response: ResponsesAPIResponse = (
                LoveEngineCompletionResponsesConfig.transform_chat_completion_response_to_responses_api_response(
                    chat_completion_response=love_engine_completion_response,
                    request_input=input,
                    responses_api_request=responses_api_request,
                )
            )

            return responses_api_response

        elif isinstance(love_engine_completion_response, love_engine.CustomStreamWrapper):
            return LoveEngineCompletionStreamingIterator(
                model=model,
                love_engine_custom_stream_wrapper=love_engine_completion_response,
                request_input=input,
                responses_api_request=responses_api_request,
                custom_llm_provider=custom_llm_provider,
                love_engine_metadata=kwargs.get("love_engine_metadata", {}),
            )
        raise ValueError(
            f"Unexpected response type: {type(love_engine_completion_response)}"
        )

    async def async_response_api_handler(
        self,
        love_engine_completion_request: dict,
        request_input: Union[str, ResponseInputParam],
        responses_api_request: ResponsesAPIOptionalRequestParams,
        **kwargs,
    ) -> Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]:
        previous_response_id: Optional[str] = responses_api_request.get(
            "previous_response_id"
        )
        if previous_response_id:
            love_engine_completion_request = await LoveEngineCompletionResponsesConfig.async_responses_api_session_handler(
                previous_response_id=previous_response_id,
                love_engine_completion_request=love_engine_completion_request,
            )

        acompletion_args = {}
        acompletion_args.update(kwargs)
        acompletion_args.update(love_engine_completion_request)

        love_engine_completion_response: Union[
            ModelResponse, love_engine.CustomStreamWrapper
        ] = await love_engine.acompletion(
            **acompletion_args,
        )

        if isinstance(love_engine_completion_response, ModelResponse):
            responses_api_response: ResponsesAPIResponse = (
                LoveEngineCompletionResponsesConfig.transform_chat_completion_response_to_responses_api_response(
                    chat_completion_response=love_engine_completion_response,
                    request_input=request_input,
                    responses_api_request=responses_api_request,
                )
            )

            return responses_api_response

        elif isinstance(love_engine_completion_response, love_engine.CustomStreamWrapper):
            return LoveEngineCompletionStreamingIterator(
                model=love_engine_completion_request.get("model") or "",
                love_engine_custom_stream_wrapper=love_engine_completion_response,
                request_input=request_input,
                responses_api_request=responses_api_request,
                custom_llm_provider=love_engine_completion_request.get(
                    "custom_llm_provider"
                ),
                love_engine_metadata=kwargs.get("love_engine_metadata", {}),
            )
        raise ValueError(
            f"Unexpected response type: {type(love_engine_completion_response)}"
        )
