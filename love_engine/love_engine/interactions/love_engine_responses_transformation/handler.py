"""
Handler for transforming interactions API requests to love_engine.responses requests.
"""

from typing import (
    Any,
    AsyncIterator,
    Coroutine,
    Dict,
    Iterator,
    Optional,
    Union,
    cast,
)

import love_engine
from love_engine.interactions.love_engine_responses_transformation.streaming_iterator import (
    LoveEngineResponsesInteractionsStreamingIterator,
)
from love_engine.interactions.love_engine_responses_transformation.transformation import (
    LoveEngineResponsesInteractionsConfig,
)
from love_engine.responses.streaming_iterator import BaseResponsesAPIStreamingIterator
from love_engine.types.interactions import (
    InteractionInput,
    InteractionsAPIOptionalRequestParams,
    InteractionsAPIResponse,
    InteractionsAPIStreamingResponse,
)
from love_engine.types.llms.openai import ResponsesAPIResponse


class LoveEngineResponsesInteractionsHandler:
    """Handler for bridging Interactions API to Responses API via love_engine.responses()."""

    def interactions_api_handler(
        self,
        model: str,
        input: Optional[InteractionInput],
        optional_params: InteractionsAPIOptionalRequestParams,
        custom_llm_provider: Optional[str] = None,
        _is_async: bool = False,
        stream: Optional[bool] = None,
        **kwargs,
    ) -> Union[
        InteractionsAPIResponse,
        Iterator[InteractionsAPIStreamingResponse],
        Coroutine[
            Any,
            Any,
            Union[
                InteractionsAPIResponse,
                AsyncIterator[InteractionsAPIStreamingResponse],
            ],
        ],
    ]:
        """
        Handle Interactions API request by calling love_engine.responses().

        Args:
            model: The model to use
            input: The input content
            optional_params: Optional parameters for the request
            custom_llm_provider: Override LLM provider
            _is_async: Whether this is an async call
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            InteractionsAPIResponse or streaming iterator
        """
        # Transform interactions request to responses request
        responses_request = LoveEngineResponsesInteractionsConfig.transform_interactions_request_to_responses_request(
            model=model,
            input=input,
            optional_params=optional_params,
            custom_llm_provider=custom_llm_provider,
            stream=stream,
            **kwargs,
        )

        if _is_async:
            return self.async_interactions_api_handler(
                responses_request=responses_request,
                model=model,
                input=input,
                optional_params=optional_params,
                **kwargs,
            )

        # Call love_engine.responses()
        # Note: love_engine.responses() returns Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]
        # but the type checker may see it as a coroutine in some contexts
        responses_response = love_engine.responses(
            **responses_request,
        )

        # Handle streaming response
        if isinstance(responses_response, BaseResponsesAPIStreamingIterator):
            return LoveEngineResponsesInteractionsStreamingIterator(
                model=model,
                love_engine_custom_stream_wrapper=responses_response,
                request_input=input,
                optional_params=optional_params,
                custom_llm_provider=custom_llm_provider,
                love_engine_metadata=kwargs.get("love_engine_metadata", {}),
            )

        # At this point, responses_response must be ResponsesAPIResponse (not streaming)
        # Cast to satisfy type checker since we've already checked it's not a streaming iterator
        responses_api_response = cast(ResponsesAPIResponse, responses_response)

        # Transform responses response to interactions response
        return LoveEngineResponsesInteractionsConfig.transform_responses_response_to_interactions_response(
            responses_response=responses_api_response,
            model=model,
        )

    async def async_interactions_api_handler(
        self,
        responses_request: Dict[str, Any],
        model: str,
        input: Optional[InteractionInput],
        optional_params: InteractionsAPIOptionalRequestParams,
        **kwargs,
    ) -> Union[
        InteractionsAPIResponse, AsyncIterator[InteractionsAPIStreamingResponse]
    ]:
        """Async handler for interactions API requests."""
        # Call love_engine.aresponses()
        # Note: love_engine.aresponses() returns Union[ResponsesAPIResponse, BaseResponsesAPIStreamingIterator]
        responses_response = await love_engine.aresponses(
            **responses_request,
        )

        # Handle streaming response
        if isinstance(responses_response, BaseResponsesAPIStreamingIterator):
            return LoveEngineResponsesInteractionsStreamingIterator(
                model=model,
                love_engine_custom_stream_wrapper=responses_response,
                request_input=input,
                optional_params=optional_params,
                custom_llm_provider=responses_request.get("custom_llm_provider"),
                love_engine_metadata=kwargs.get("love_engine_metadata", {}),
            )

        # At this point, responses_response must be ResponsesAPIResponse (not streaming)
        # Cast to satisfy type checker since we've already checked it's not a streaming iterator
        responses_api_response = cast(ResponsesAPIResponse, responses_response)

        # Transform responses response to interactions response
        return LoveEngineResponsesInteractionsConfig.transform_responses_response_to_interactions_response(
            responses_response=responses_api_response,
            model=model,
        )
