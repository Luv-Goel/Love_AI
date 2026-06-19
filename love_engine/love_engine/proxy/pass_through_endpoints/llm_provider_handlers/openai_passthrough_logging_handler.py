"""
OpenAI Passthrough Logging Handler

Handles cost tracking and logging for OpenAI passthrough endpoints, specifically /chat/completions.
"""

from datetime import datetime
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse

import httpx

import love_engine
from love_engine._logging import verbose_proxy_logger
from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
from love_engine.love_engine_core_utils.love_engine_logging import (
    get_standard_logging_object_payload,
)
from love_engine.llms.openai.openai import OpenAIConfig
from love_engine.llms.openai.openai import OpenAIConfig as OpenAIConfigType
from love_engine.llms.openai.responses.transformation import OpenAIResponsesAPIConfig
from love_engine.proxy._types import PassThroughEndpointLoggingTypedDict
from love_engine.proxy.pass_through_endpoints.llm_provider_handlers.base_passthrough_logging_handler import (
    BasePassthroughLoggingHandler,
)
from love_engine.proxy.pass_through_endpoints.success_handler import (
    PassThroughEndpointLogging,
)
from love_engine.types.passthrough_endpoints.pass_through_endpoints import (
    EndpointType,
    PassthroughStandardLoggingPayload,
)
from love_engine.types.llms.openai import ResponsesAPIResponse
from love_engine.types.utils import ImageResponse, LlmProviders, PassthroughCallTypes
from love_engine.utils import ModelResponse, TextCompletionResponse

# Hostnames that route to OpenAI-compatible APIs.
#
# `api.openai.com` is OpenAI proper. The two Azure domains below are *shared by
# every Azure Cognitive Service* (Speech, Vision, Language, ...), not just Azure
# OpenAI: `openai.azure.com` is the classic Azure OpenAI domain, while
# `cognitiveservices.azure.com` is used by newer "Azure AI Foundry" /
# Cognitive Services-hosted Azure OpenAI deployments. Because the hostname alone
# cannot tell Azure OpenAI apart from the other Cognitive Services on those
# domains, requests there must additionally carry an OpenAI-style path segment.
_OPENAI_HOSTNAMES = ("api.openai.com",)
_AZURE_OPENAI_HOSTNAMES = ("openai.azure.com", "cognitiveservices.azure.com")
# Path markers that identify an Azure request as Azure OpenAI rather than Speech
# / Vision / Language / ... `/openai/` is the native Azure OpenAI path prefix;
# `/v1/` is the OpenAI-v1 surface used by LoveEngine's pass-through routing. Other
# Cognitive Services use service-named prefixes and versions like `/v3.1/`,
# `/v1.0/`, so they do not collide with these markers.
_AZURE_OPENAI_PATH_MARKERS = ("/openai/", "/v1/")


def _hostname_matches(hostname: str, suffixes: tuple) -> bool:
    """True if hostname equals one of `suffixes` or is a subdomain of it.

    Uses suffix matching (not a bare substring test) so look-alikes such as
    `cognitiveservices.azure.com.attacker.example` are not accepted.
    """
    return any(
        hostname == suffix or hostname.endswith("." + suffix) for suffix in suffixes
    )


def _is_openai_compatible_host(hostname: Optional[str]) -> bool:
    """True if the hostname is OpenAI proper or one of the Azure OpenAI domains.

    Hostname-only check, kept for the route-level helpers that additionally
    require a specific OpenAI path (e.g. `/v1/chat/completions`). When only the
    hostname would otherwise gate dispatch, use `_is_openai_compatible_url` so
    non-OpenAI Azure Cognitive Services on the shared domains are excluded.
    """
    if not hostname:
        return False
    return _hostname_matches(hostname, _OPENAI_HOSTNAMES) or _hostname_matches(
        hostname, _AZURE_OPENAI_HOSTNAMES
    )


def _is_openai_compatible_url(url_route: Optional[str]) -> bool:
    """True if the URL targets an OpenAI-compatible API surface.

    For the shared Azure Cognitive Services domains we additionally require an
    OpenAI-style path segment (`/openai/` or `/v1/`) so non-OpenAI Azure services
    (Speech, Vision, Language, ...) on the same domain are not misclassified as
    OpenAI routes.
    """
    if not url_route:
        return False
    parsed_url = urlparse(url_route)
    hostname = parsed_url.hostname
    if not hostname:
        return False
    if _hostname_matches(hostname, _OPENAI_HOSTNAMES):
        return True
    if _hostname_matches(hostname, _AZURE_OPENAI_HOSTNAMES):
        return any(marker in parsed_url.path for marker in _AZURE_OPENAI_PATH_MARKERS)
    return False


class OpenAIPassthroughLoggingHandler(BasePassthroughLoggingHandler):
    """
    OpenAI-specific passthrough logging handler that provides cost tracking for /chat/completions endpoints.
    """

    @property
    def llm_provider_name(self) -> LlmProviders:
        return LlmProviders.OPENAI

    def get_provider_config(self, model: str) -> OpenAIConfigType:
        """Get OpenAI provider configuration for the given model."""
        return OpenAIConfig()

    @staticmethod
    def is_openai_chat_completions_route(url_route: str) -> bool:
        """Check if the URL route is an OpenAI chat completions endpoint."""
        if not url_route:
            return False
        parsed_url = urlparse(url_route)
        return (
            _is_openai_compatible_host(parsed_url.hostname)
            and "/v1/chat/completions" in parsed_url.path
        )

    @staticmethod
    def is_openai_image_generation_route(url_route: str) -> bool:
        """Check if the URL route is an OpenAI image generation endpoint."""
        if not url_route:
            return False
        parsed_url = urlparse(url_route)
        return (
            _is_openai_compatible_host(parsed_url.hostname)
            and "/v1/images/generations" in parsed_url.path
        )

    @staticmethod
    def is_openai_image_editing_route(url_route: str) -> bool:
        """Check if the URL route is an OpenAI image editing endpoint."""
        if not url_route:
            return False
        parsed_url = urlparse(url_route)
        return (
            _is_openai_compatible_host(parsed_url.hostname)
            and "/v1/images/edits" in parsed_url.path
        )

    @staticmethod
    def is_openai_responses_route(url_route: str) -> bool:
        """Check if the URL route is an OpenAI responses API endpoint."""
        if not url_route:
            return False
        parsed_url = urlparse(url_route)
        return _is_openai_compatible_host(parsed_url.hostname) and (
            "/v1/responses" in parsed_url.path or "/responses" in parsed_url.path
        )

    def _get_user_from_metadata(
        self,
        passthrough_logging_payload: PassthroughStandardLoggingPayload,
    ) -> Optional[str]:
        """Extract user information from passthrough logging payload."""
        request_body = passthrough_logging_payload.get("request_body")
        if request_body:
            return request_body.get("user")
        return None

    @staticmethod
    def _calculate_image_generation_cost(
        model: str,
        response_body: dict,
        request_body: dict,
    ) -> float:
        """Calculate cost for OpenAI image generation."""
        try:
            # Extract parameters from request
            n = request_body.get("n", 1)
            try:
                n = int(n)
            except Exception:
                n = 1
            size = request_body.get("size", "1024x1024")
            quality = request_body.get("quality", None)

            # Use LoveEngine's default image cost calculator
            from love_engine.cost_calculator import default_image_cost_calculator

            cost = default_image_cost_calculator(
                model=model,
                custom_llm_provider="openai",
                quality=quality,
                n=n,
                size=size,
                optional_params=request_body,
            )

            return cost
        except Exception as e:
            verbose_proxy_logger.warning(
                f"Error calculating image generation cost: {str(e)}"
            )
            return 0.0

    @staticmethod
    def _calculate_image_editing_cost(
        model: str,
        response_body: dict,
        request_body: dict,
    ) -> float:
        """Calculate cost for OpenAI image editing."""
        try:
            # Extract parameters from request
            n = request_body.get("n", 1)
            # Image edit typically uses multipart/form-data (because of files), so all fields arrive as strings (e.g., n = "1").
            try:
                n = int(n)
            except Exception:
                n = 1
            size = request_body.get("size", "1024x1024")

            # Use LoveEngine's default image cost calculator
            from love_engine.cost_calculator import default_image_cost_calculator

            cost = default_image_cost_calculator(
                model=model,
                custom_llm_provider="openai",
                quality=None,  # Image editing doesn't have quality parameter
                n=n,
                size=size,
                optional_params=request_body,
            )

            return cost
        except Exception as e:
            verbose_proxy_logger.warning(
                f"Error calculating image editing cost: {str(e)}"
            )
            return 0.0

    @staticmethod
    def _build_responses_api_response_and_cost(
        model: str,
        httpx_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
        custom_llm_provider: str,
    ) -> Tuple[ResponsesAPIResponse, float]:
        """Transform a Responses API raw response into a ResponsesAPIResponse
        and compute its cost.

        The Responses API has a different on-the-wire shape from chat
        completions (`output: [...]` instead of `choices: [...]`), so the
        chat-completions `transform_response` raises KeyError 'choices' on
        a Responses payload. Use the dedicated Responses-API transformer
        (`OpenAIResponsesAPIConfig.transform_response_api_response`) here.

        Returns (love_engine_model_response, response_cost) — symmetric with the
        chat-completions branch which produces the same two values inline,
        and analogous to the image branches' `_calculate_image_*_cost` helpers
        (which return cost only because the image-response object is trivial
        to build inline; the Responses payload needs a real transformer).
        """
        responses_config = OpenAIResponsesAPIConfig()
        love_engine_model_response = responses_config.transform_response_api_response(
            model=model,
            raw_response=httpx_response,
            logging_obj=logging_obj,
        )
        response_cost = love_engine.completion_cost(
            completion_response=love_engine_model_response,
            model=model,
            custom_llm_provider=custom_llm_provider,
            call_type="responses",
        )
        return love_engine_model_response, response_cost

    @staticmethod
    def openai_passthrough_handler(
        httpx_response: httpx.Response,
        response_body: dict,
        logging_obj: LoveEngineLoggingObj,
        url_route: str,
        result: str,
        start_time: datetime,
        end_time: datetime,
        cache_hit: bool,
        request_body: dict,
        **kwargs,
    ) -> PassThroughEndpointLoggingTypedDict:
        """
        Handle OpenAI passthrough logging with cost tracking for chat completions, image generation, image editing, and responses API.
        """
        # Check if this is a supported endpoint for cost tracking
        is_chat_completions = (
            OpenAIPassthroughLoggingHandler.is_openai_chat_completions_route(url_route)
        )
        is_image_generation = (
            OpenAIPassthroughLoggingHandler.is_openai_image_generation_route(url_route)
        )
        is_image_editing = (
            OpenAIPassthroughLoggingHandler.is_openai_image_editing_route(url_route)
        )
        is_responses = OpenAIPassthroughLoggingHandler.is_openai_responses_route(
            url_route
        )

        if not (
            is_chat_completions
            or is_image_generation
            or is_image_editing
            or is_responses
        ):
            # For unsupported endpoints, return None to let the system fall back to generic behavior
            return {
                "result": None,
                "kwargs": kwargs,
            }

        # Extract model from request or response
        model = request_body.get("model", response_body.get("model", ""))
        if not model:
            verbose_proxy_logger.warning(
                "No model found in request or response for OpenAI passthrough cost tracking"
            )
            base_handler = OpenAIPassthroughLoggingHandler()
            return base_handler.passthrough_chat_handler(
                httpx_response=httpx_response,
                response_body=response_body,
                logging_obj=logging_obj,
                url_route=url_route,
                result=result,
                start_time=start_time,
                end_time=end_time,
                cache_hit=cache_hit,
                request_body=request_body,
                **kwargs,
            )

        try:
            response_cost = 0.0
            love_engine_model_response: Optional[
                Union[
                    ModelResponse,
                    TextCompletionResponse,
                    ImageResponse,
                    ResponsesAPIResponse,
                ]
            ] = None
            handler_instance = OpenAIPassthroughLoggingHandler()

            custom_llm_provider = kwargs.get("custom_llm_provider", "openai")

            if is_chat_completions:
                # Handle chat completions with existing logic
                provider_config = handler_instance.get_provider_config(model=model)
                # Preserve existing love_engine_params to maintain metadata tags
                existing_love_engine_params = kwargs.get("love_engine_params", {}) or {}
                love_engine_model_response = provider_config.transform_response(
                    raw_response=httpx_response,
                    model_response=love_engine.ModelResponse(),
                    model=model,
                    messages=request_body.get("messages", []),
                    logging_obj=logging_obj,
                    optional_params=request_body.get("optional_params", {}),
                    api_key="",
                    request_data=request_body,
                    encoding=love_engine.encoding,
                    json_mode=request_body.get("response_format", {}).get("type")
                    == "json_object",
                    love_engine_params=existing_love_engine_params,
                )

                # Calculate cost using LoveEngine's cost calculator
                response_cost = love_engine.completion_cost(
                    completion_response=love_engine_model_response,
                    model=model,
                    custom_llm_provider=custom_llm_provider,
                )
            elif is_image_generation:
                # Handle image generation cost calculation
                response_cost = (
                    OpenAIPassthroughLoggingHandler._calculate_image_generation_cost(
                        model=model,
                        response_body=response_body,
                        request_body=request_body,
                    )
                )
                # Mark call type for downstream image-aware logic/metrics
                try:
                    logging_obj.call_type = (
                        PassthroughCallTypes.passthrough_image_generation.value
                    )
                except Exception:
                    pass
                # Create a simple response object for logging
                love_engine_model_response = ImageResponse(
                    data=response_body.get("data", []),
                    model=model,
                )
                # Set the calculated cost in _hidden_params to prevent recalculation
                if not hasattr(love_engine_model_response, "_hidden_params"):
                    love_engine_model_response._hidden_params = {}
                love_engine_model_response._hidden_params["response_cost"] = response_cost
            elif is_image_editing:
                # Handle image editing cost calculation
                response_cost = (
                    OpenAIPassthroughLoggingHandler._calculate_image_editing_cost(
                        model=model,
                        response_body=response_body,
                        request_body=request_body,
                    )
                )
                # Mark call type for downstream image-aware logic/metrics
                try:
                    logging_obj.call_type = (
                        PassthroughCallTypes.passthrough_image_generation.value
                    )
                except Exception:
                    pass
                # Create a simple response object for logging
                love_engine_model_response = ImageResponse(
                    data=response_body.get("data", []),
                    model=model,
                )
                # Set the calculated cost in _hidden_params to prevent recalculation
                if not hasattr(love_engine_model_response, "_hidden_params"):
                    love_engine_model_response._hidden_params = {}
                love_engine_model_response._hidden_params["response_cost"] = response_cost
            elif is_responses:
                # Responses-API cost tracking — see
                # `_build_responses_api_response_and_cost` for why this needs
                # a dedicated transformer (the chat-completions transform
                # crashes on the Responses payload shape).
                (
                    love_engine_model_response,
                    response_cost,
                ) = OpenAIPassthroughLoggingHandler._build_responses_api_response_and_cost(
                    model=model,
                    httpx_response=httpx_response,
                    logging_obj=logging_obj,
                    custom_llm_provider=custom_llm_provider,
                )

            # Update kwargs with cost information
            kwargs["response_cost"] = response_cost
            kwargs["model"] = model
            kwargs["custom_llm_provider"] = custom_llm_provider

            # Extract user information for tracking
            passthrough_logging_payload: Optional[PassthroughStandardLoggingPayload] = (
                kwargs.get("passthrough_logging_payload")
            )
            if passthrough_logging_payload:
                user = handler_instance._get_user_from_metadata(
                    passthrough_logging_payload=passthrough_logging_payload,
                )
                if user:
                    kwargs["love_engine_params"].setdefault(
                        "proxy_server_request", {}
                    ).setdefault("body", {})["user"] = user

            # Create standard logging object
            if love_engine_model_response is not None:
                get_standard_logging_object_payload(
                    kwargs=kwargs,
                    init_response_obj=love_engine_model_response,
                    start_time=start_time,
                    end_time=end_time,
                    logging_obj=logging_obj,
                    status="success",
                )

            # Update logging object with cost information
            logging_obj.model_call_details["model"] = model
            logging_obj.model_call_details["custom_llm_provider"] = custom_llm_provider
            logging_obj.model_call_details["response_cost"] = response_cost

            endpoint_type = (
                "chat_completions"
                if is_chat_completions
                else "image_generation" if is_image_generation else "image_editing"
            )
            verbose_proxy_logger.debug(
                f"OpenAI passthrough cost tracking - Endpoint: {endpoint_type}, Model: {model}, Cost: ${response_cost:.6f}"
            )

            return {
                "result": love_engine_model_response,
                "kwargs": kwargs,
            }

        except Exception as e:
            verbose_proxy_logger.error(
                f"Error in OpenAI passthrough cost tracking: {str(e)}"
            )
            # Fall back to base handler without cost tracking
            base_handler = OpenAIPassthroughLoggingHandler()
            return base_handler.passthrough_chat_handler(
                httpx_response=httpx_response,
                response_body=response_body,
                logging_obj=logging_obj,
                url_route=url_route,
                result=result,
                start_time=start_time,
                end_time=end_time,
                cache_hit=cache_hit,
                request_body=request_body,
                **kwargs,
            )

    def _build_complete_streaming_response(
        self,
        all_chunks: list,
        love_engine_logging_obj: LoveEngineLoggingObj,
        model: str,
    ) -> Optional[Union[ModelResponse, TextCompletionResponse]]:
        """
        Builds complete response from raw chunks for OpenAI streaming responses.

        - Converts str chunks to generic chunks
        - Converts generic chunks to love_engine chunks (OpenAI format)
        - Builds complete response from love_engine chunks
        """
        try:
            # OpenAI's response iterator to parse chunks
            from love_engine.llms.openai.openai import OpenAIChatCompletionResponseIterator

            openai_iterator = OpenAIChatCompletionResponseIterator(
                streaming_response=None,
                sync_stream=False,
            )

            all_openai_chunks = []
            for chunk_str in all_chunks:
                try:
                    # Parse the string chunk using the base iterator's string parser
                    from love_engine.llms.base_llm.base_model_iterator import (
                        BaseModelResponseIterator,
                    )

                    # Convert string chunk to dict
                    stripped_json_chunk = (
                        BaseModelResponseIterator._string_to_dict_parser(
                            str_line=chunk_str
                        )
                    )

                    if stripped_json_chunk:
                        # Parse the chunk using OpenAI's chunk parser
                        transformed_chunk = openai_iterator.chunk_parser(
                            chunk=stripped_json_chunk
                        )
                        if transformed_chunk is not None:
                            all_openai_chunks.append(transformed_chunk)

                except (StopIteration, StopAsyncIteration, Exception) as e:
                    verbose_proxy_logger.debug(f"Error parsing streaming chunk: {e}")
                    continue

            if not all_openai_chunks:
                verbose_proxy_logger.warning(
                    "No valid chunks found in streaming response"
                )
                return None

            # Build complete response from chunks
            complete_streaming_response = love_engine.stream_chunk_builder(
                chunks=all_openai_chunks
            )

            return complete_streaming_response

        except Exception as e:
            verbose_proxy_logger.error(
                f"Error building complete streaming response: {str(e)}"
            )
            return None

    @staticmethod
    def _handle_logging_openai_collected_chunks(
        love_engine_logging_obj: LoveEngineLoggingObj,
        passthrough_success_handler_obj: PassThroughEndpointLogging,
        url_route: str,
        request_body: dict,
        endpoint_type: EndpointType,
        start_time: datetime,
        all_chunks: List[str],
        end_time: datetime,
    ) -> PassThroughEndpointLoggingTypedDict:
        """
        Handle logging for collected OpenAI streaming chunks with cost tracking.
        """
        try:
            # Extract model from request body
            model = request_body.get("model", "gpt-4o")

            # Build complete response from chunks using our streaming handler
            handler = OpenAIPassthroughLoggingHandler()
            handler_instance = handler
            complete_response = handler._build_complete_streaming_response(
                all_chunks=all_chunks,
                love_engine_logging_obj=love_engine_logging_obj,
                model=model,
            )

            if complete_response is None:
                verbose_proxy_logger.warning(
                    "Failed to build complete response from OpenAI streaming chunks"
                )
                return {
                    "result": None,
                    "kwargs": {},
                }

            custom_llm_provider = love_engine_logging_obj.model_call_details.get(
                "custom_llm_provider", "openai"
            )
            # Calculate cost using LoveEngine's cost calculator
            response_cost = love_engine.completion_cost(
                completion_response=complete_response,
                model=model,
                custom_llm_provider=custom_llm_provider,
            )

            # Preserve existing love_engine_params to maintain metadata tags
            existing_love_engine_params = (
                love_engine_logging_obj.model_call_details.get("love_engine_params", {}) or {}
            )

            # Prepare kwargs for logging
            kwargs = {
                "response_cost": response_cost,
                "model": model,
                "custom_llm_provider": custom_llm_provider,
                "love_engine_params": existing_love_engine_params.copy(),
            }

            # Extract user information for tracking
            passthrough_logging_payload: Optional[PassthroughStandardLoggingPayload] = (
                love_engine_logging_obj.model_call_details.get(
                    "passthrough_logging_payload"
                )
            )
            if passthrough_logging_payload:
                user = handler_instance._get_user_from_metadata(
                    passthrough_logging_payload=passthrough_logging_payload,
                )
                if user:
                    kwargs["love_engine_params"].setdefault(
                        "proxy_server_request", {}
                    ).setdefault("body", {})["user"] = user

            # Create standard logging object
            get_standard_logging_object_payload(
                kwargs=kwargs,
                init_response_obj=complete_response,
                start_time=start_time,
                end_time=end_time,
                logging_obj=love_engine_logging_obj,
                status="success",
            )

            # Update logging object with cost information
            love_engine_logging_obj.model_call_details["model"] = model
            love_engine_logging_obj.model_call_details["custom_llm_provider"] = (
                custom_llm_provider
            )
            love_engine_logging_obj.model_call_details["response_cost"] = response_cost

            verbose_proxy_logger.debug(
                f"OpenAI streaming passthrough cost tracking - Model: {model}, Cost: ${response_cost:.6f}"
            )

            return {
                "result": complete_response,
                "kwargs": kwargs,
            }

        except Exception as e:
            verbose_proxy_logger.error(
                f"Error in OpenAI streaming passthrough cost tracking: {str(e)}"
            )
            return {
                "result": None,
                "kwargs": {},
            }
