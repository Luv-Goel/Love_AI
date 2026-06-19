"""
Main File for Batches API implementation

https://platform.openai.com/docs/api-reference/batch

- create_batch()
- retrieve_batch()
- cancel_batch()
- list_batch()

"""

import asyncio
import contextvars
import os
from functools import partial
from typing import Any, Coroutine, Dict, Literal, Optional, Union, cast

import httpx
from openai.types.batch import BatchRequestCounts

import love_engine
from love_engine._logging import verbose_logger
from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
from love_engine.llms.anthropic.batches.handler import AnthropicBatchesHandler
from love_engine.llms.azure.batches.handler import AzureBatchesAPI
from love_engine.llms.bedrock.batches.handler import BedrockBatchesHandler
from love_engine.llms.custom_httpx.http_handler import AsyncHTTPHandler, HTTPHandler
from love_engine.llms.custom_httpx.llm_http_handler import BaseLLMHTTPHandler
from love_engine.llms.openai.openai import OpenAIBatchesAPI
from love_engine.llms.vertex_ai.batches.handler import VertexAIBatchPrediction
from love_engine.secret_managers.main import get_secret_str
from love_engine.types.llms.openai import (
    CancelBatchRequest,
    CreateBatchRequest,
    FileExpiresAfter,
    RetrieveBatchRequest,
)
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import (
    LIST_BATCHES_SUPPORTED_PROVIDERS,
    OPENAI_COMPATIBLE_BATCH_AND_FILES_PROVIDERS,
    ListBatchesSupportedProvider,
    LoveEngineBatch,
    LlmProviders,
)
from love_engine.utils import (
    ProviderConfigManager,
    client,
    get_love_engine_params,
    get_llm_provider,
    supports_httpx_timeout,
)

####### ENVIRONMENT VARIABLES ###################
openai_batches_instance = OpenAIBatchesAPI()
azure_batches_instance = AzureBatchesAPI()
vertex_ai_batches_instance = VertexAIBatchPrediction(gcs_bucket_name="")
anthropic_batches_instance = AnthropicBatchesHandler()
base_llm_http_handler = BaseLLMHTTPHandler()
#################################################


def _resolve_timeout(
    optional_params: GenericLoveEngineParams,
    kwargs: Dict[str, Any],
    custom_llm_provider: str,
    default_timeout: float = 600.0,
) -> float:
    """
    Resolve timeout value from various sources and handle httpx.Timeout objects.

    Args:
        optional_params: GenericLoveEngineParams object containing timeout
        kwargs: Additional kwargs that may contain request_timeout
        custom_llm_provider: Provider name for httpx timeout support check
        default_timeout: Default timeout value to use

    Returns:
        Resolved timeout as float
    """
    timeout = (
        optional_params.timeout
        or kwargs.get("request_timeout", default_timeout)
        or default_timeout
    )

    # Handle httpx.Timeout objects
    if isinstance(timeout, httpx.Timeout):
        if supports_httpx_timeout(custom_llm_provider) is False:
            # Extract read timeout for providers that don't support httpx.Timeout
            read_timeout = timeout.read or default_timeout
            return float(read_timeout)
        else:
            # For providers that support httpx.Timeout, we still need to return a float
            # This case might need to be handled differently based on the actual use case
            return float(timeout.read or default_timeout)

    # Handle None case
    if timeout is None:
        return float(default_timeout)

    # Handle numeric values (int, float, string representations)
    return float(timeout)


@client
async def acreate_batch(
    completion_window: Literal["24h"],
    endpoint: Literal["/v1/chat/completions", "/v1/embeddings", "/v1/completions"],
    input_file_id: str,
    custom_llm_provider: Literal[
        "openai", "azure", "vertex_ai", "bedrock", "hosted_vllm"
    ] = "openai",
    metadata: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    output_expires_after: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> LoveEngineBatch:
    """
    Async: Creates and executes a batch from an uploaded file of request

    love_engine Equivalent of POST: https://api.openai.com/v1/batches
    """
    try:
        loop = asyncio.get_event_loop()
        kwargs["acreate_batch"] = True

        # Use a partial function to pass your keyword arguments
        func = partial(
            create_batch,
            completion_window,
            endpoint,
            input_file_id,
            custom_llm_provider,
            metadata,
            extra_headers,
            extra_body,
            output_expires_after,
            **kwargs,
        )

        # Add the context to the function
        ctx = contextvars.copy_context()
        func_with_context = partial(ctx.run, func)
        init_response = await loop.run_in_executor(None, func_with_context)

        if asyncio.iscoroutine(init_response):
            response = await init_response
        else:
            response = init_response

        return response
    except Exception as e:
        raise e


@client
def create_batch(
    completion_window: Literal["24h"],
    endpoint: Literal["/v1/chat/completions", "/v1/embeddings", "/v1/completions"],
    input_file_id: str,
    custom_llm_provider: Literal[
        "openai", "azure", "vertex_ai", "bedrock", "hosted_vllm"
    ] = "openai",
    metadata: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    output_expires_after: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Union[LoveEngineBatch, Coroutine[Any, Any, LoveEngineBatch]]:
    """
    Creates and executes a batch from an uploaded file of request

    love_engine Equivalent of POST: https://api.openai.com/v1/batches
    """
    try:
        optional_params = GenericLoveEngineParams(**kwargs)
        love_engine_call_id = kwargs.get("love_engine_call_id", None)
        proxy_server_request = kwargs.get("proxy_server_request", None)
        model_info = kwargs.get("model_info", None)
        model: Optional[str] = kwargs.get("model", None)
        try:
            if model is not None:
                model, _, _, _ = get_llm_provider(
                    model=model,
                    custom_llm_provider=None,
                )
        except Exception as e:
            verbose_logger.exception(
                f"love_engine.batches.main.py::create_batch() - Error inferring custom_llm_provider - {str(e)}"
            )

        _is_async = kwargs.pop("acreate_batch", False) is True
        love_engine_params = dict(GenericLoveEngineParams(**kwargs))
        love_engine_logging_obj: LoveEngineLoggingObj = cast(
            LoveEngineLoggingObj, kwargs.get("love_engine_logging_obj", None)
        )
        ### TIMEOUT LOGIC ###
        timeout = _resolve_timeout(optional_params, kwargs, custom_llm_provider)
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model=model,
            user=None,
            optional_params=optional_params.model_dump(),
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
                "proxy_server_request": proxy_server_request,
                "model_info": model_info,
                "preset_cache_key": None,
                "stream_response": {},
                **optional_params.model_dump(exclude_unset=True),
            },
            custom_llm_provider=custom_llm_provider,
        )

        _create_batch_request = CreateBatchRequest(
            completion_window=completion_window,
            endpoint=endpoint,
            input_file_id=input_file_id,
            metadata=metadata,
            extra_headers=extra_headers,
            extra_body=extra_body,
        )
        if output_expires_after is not None:
            _create_batch_request["output_expires_after"] = cast(
                FileExpiresAfter, output_expires_after
            )
        if model is not None:
            provider_config = ProviderConfigManager.get_provider_batches_config(
                model=model,
                provider=LlmProviders(custom_llm_provider),
            )
        else:
            provider_config = None
        if provider_config is not None:
            response = base_llm_http_handler.create_batch(
                provider_config=provider_config,
                love_engine_params=love_engine_params,
                create_batch_data=_create_batch_request,
                headers=extra_headers or {},
                api_base=optional_params.api_base,
                api_key=optional_params.api_key,
                logging_obj=love_engine_logging_obj,
                _is_async=_is_async,
                client=(
                    client
                    if client is not None
                    and isinstance(client, (HTTPHandler, AsyncHTTPHandler))
                    else None
                ),
                timeout=timeout,
                model=model,
            )
            return response
        api_base: Optional[str] = None
        if custom_llm_provider in OPENAI_COMPATIBLE_BATCH_AND_FILES_PROVIDERS:
            # for deepinfra/perplexity/anyscale/groq we check in get_llm_provider and pass in the api base from there
            api_base = (
                optional_params.api_base
                or love_engine.api_base
                or os.getenv("OPENAI_BASE_URL")
                or os.getenv("OPENAI_API_BASE")
                or "https://api.openai.com/v1"
            )
            organization = (
                optional_params.organization
                or love_engine.organization
                or os.getenv("OPENAI_ORGANIZATION", None)
                or None  # default - https://github.com/openai/openai-python/blob/284c1799070c723c6a553337134148a7ab088dd8/openai/util.py#L105
            )
            # set API KEY
            api_key = (
                optional_params.api_key
                or love_engine.api_key  # for deepinfra/perplexity/anyscale we check in get_llm_provider and pass in the api key from there
                or love_engine.openai_key
                or os.getenv("OPENAI_API_KEY")
            )

            response = openai_batches_instance.create_batch(
                api_base=api_base,
                api_key=api_key,
                organization=organization,
                create_batch_data=_create_batch_request,
                timeout=timeout,
                max_retries=optional_params.max_retries,
                _is_async=_is_async,
            )
        elif custom_llm_provider == "azure":
            api_base = (
                optional_params.api_base
                or love_engine.api_base
                or get_secret_str("AZURE_API_BASE")
            )
            api_version = (
                optional_params.api_version
                or love_engine.api_version
                or get_secret_str("AZURE_API_VERSION")
            )

            api_key = (
                optional_params.api_key
                or love_engine.api_key
                or love_engine.azure_key
                or get_secret_str("AZURE_OPENAI_API_KEY")
                or get_secret_str("AZURE_API_KEY")
            )

            extra_body = optional_params.get("extra_body", {})
            if extra_body is not None:
                extra_body.pop("azure_ad_token", None)
            else:
                get_secret_str("AZURE_AD_TOKEN")  # type: ignore

            response = azure_batches_instance.create_batch(
                _is_async=_is_async,
                api_base=api_base,
                api_key=api_key,
                api_version=api_version,
                timeout=timeout,
                max_retries=optional_params.max_retries,
                create_batch_data=_create_batch_request,
                love_engine_params=love_engine_params,
            )
        elif custom_llm_provider == "vertex_ai":
            api_base = optional_params.api_base or ""
            vertex_ai_project = (
                optional_params.vertex_project
                or love_engine.vertex_project
                or get_secret_str("VERTEXAI_PROJECT")
            )
            vertex_ai_location = (
                optional_params.vertex_location
                or love_engine.vertex_location
                or get_secret_str("VERTEXAI_LOCATION")
            )
            vertex_credentials = optional_params.vertex_credentials or get_secret_str(
                "VERTEXAI_CREDENTIALS"
            )

            response = vertex_ai_batches_instance.create_batch(
                _is_async=_is_async,
                api_base=api_base,
                vertex_project=vertex_ai_project,
                vertex_location=vertex_ai_location,
                vertex_credentials=vertex_credentials,
                timeout=timeout,
                max_retries=optional_params.max_retries,
                create_batch_data=_create_batch_request,
            )
        else:
            raise love_engine.exceptions.BadRequestError(
                message="love_engine doesn't support custom_llm_provider={} for 'create_batch'".format(
                    custom_llm_provider
                ),
                model="n/a",
                llm_provider=custom_llm_provider,
                response=httpx.Response(
                    status_code=400,
                    content="Unsupported provider",
                    request=httpx.Request(method="create_batch", url="https://github.com/BerriAI/love_engine"),  # type: ignore
                ),
            )
        return response
    except Exception as e:
        raise e


@client
async def aretrieve_batch(
    batch_id: str,
    custom_llm_provider: Literal[
        "openai", "azure", "vertex_ai", "bedrock", "hosted_vllm", "anthropic"
    ] = "openai",
    metadata: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    **kwargs,
) -> LoveEngineBatch:
    """
    Async: Retrieves a batch.

    love_engine Equivalent of GET https://api.openai.com/v1/batches/{batch_id}
    """
    try:
        loop = asyncio.get_event_loop()
        kwargs["aretrieve_batch"] = True

        # Use a partial function to pass your keyword arguments
        func = partial(
            retrieve_batch,
            batch_id,
            custom_llm_provider,
            metadata,
            extra_headers,
            extra_body,
            **kwargs,
        )
        # Add the context to the function
        ctx = contextvars.copy_context()
        func_with_context = partial(ctx.run, func)
        init_response = await loop.run_in_executor(None, func_with_context)
        if asyncio.iscoroutine(init_response):
            response = await init_response
        else:
            response = init_response  # type: ignore

        return response
    except Exception as e:
        raise e


def _handle_retrieve_batch_providers_without_provider_config(
    batch_id: str,
    optional_params: GenericLoveEngineParams,
    timeout: Union[float, httpx.Timeout],
    love_engine_params: dict,
    _retrieve_batch_request: RetrieveBatchRequest,
    _is_async: bool,
    custom_llm_provider: Literal[
        "openai", "azure", "vertex_ai", "bedrock", "hosted_vllm", "anthropic"
    ] = "openai",
    logging_obj: Optional[Any] = None,
):
    api_base: Optional[str] = None
    if custom_llm_provider in OPENAI_COMPATIBLE_BATCH_AND_FILES_PROVIDERS:
        # for deepinfra/perplexity/anyscale/groq we check in get_llm_provider and pass in the api base from there
        api_base = (
            optional_params.api_base
            or love_engine.api_base
            or os.getenv("OPENAI_BASE_URL")
            or os.getenv("OPENAI_API_BASE")
            or "https://api.openai.com/v1"
        )
        organization = (
            optional_params.organization
            or love_engine.organization
            or os.getenv("OPENAI_ORGANIZATION", None)
            or None  # default - https://github.com/openai/openai-python/blob/284c1799070c723c6a553337134148a7ab088dd8/openai/util.py#L105
        )
        # set API KEY
        api_key = (
            optional_params.api_key
            or love_engine.api_key  # for deepinfra/perplexity/anyscale we check in get_llm_provider and pass in the api key from there
            or love_engine.openai_key
            or os.getenv("OPENAI_API_KEY")
        )

        response = openai_batches_instance.retrieve_batch(
            _is_async=_is_async,
            retrieve_batch_data=_retrieve_batch_request,
            api_base=api_base,
            api_key=api_key,
            organization=organization,
            timeout=timeout,
            max_retries=optional_params.max_retries,
        )
    elif custom_llm_provider == "azure":
        api_base = (
            optional_params.api_base
            or love_engine.api_base
            or get_secret_str("AZURE_API_BASE")
        )
        api_version = (
            optional_params.api_version
            or love_engine.api_version
            or get_secret_str("AZURE_API_VERSION")
        )

        api_key = (
            optional_params.api_key
            or love_engine.api_key
            or love_engine.azure_key
            or get_secret_str("AZURE_OPENAI_API_KEY")
            or get_secret_str("AZURE_API_KEY")
        )

        extra_body = optional_params.get("extra_body", {})
        if extra_body is not None:
            extra_body.pop("azure_ad_token", None)
        else:
            get_secret_str("AZURE_AD_TOKEN")  # type: ignore

        response = azure_batches_instance.retrieve_batch(
            _is_async=_is_async,
            api_base=api_base,
            api_key=api_key,
            api_version=api_version,
            timeout=timeout,
            max_retries=optional_params.max_retries,
            retrieve_batch_data=_retrieve_batch_request,
            love_engine_params=love_engine_params,
        )
    elif custom_llm_provider == "vertex_ai":
        api_base = optional_params.api_base or ""
        vertex_ai_project = (
            optional_params.vertex_project
            or love_engine.vertex_project
            or get_secret_str("VERTEXAI_PROJECT")
        )
        vertex_ai_location = (
            optional_params.vertex_location
            or love_engine.vertex_location
            or get_secret_str("VERTEXAI_LOCATION")
        )
        vertex_credentials = optional_params.vertex_credentials or get_secret_str(
            "VERTEXAI_CREDENTIALS"
        )

        response = vertex_ai_batches_instance.retrieve_batch(
            _is_async=_is_async,
            batch_id=batch_id,
            api_base=api_base,
            vertex_project=vertex_ai_project,
            vertex_location=vertex_ai_location,
            vertex_credentials=vertex_credentials,
            timeout=timeout,
            max_retries=optional_params.max_retries,
            logging_obj=logging_obj,
        )
    elif custom_llm_provider == "anthropic":
        api_base = (
            optional_params.api_base
            or love_engine.api_base
            or get_secret_str("ANTHROPIC_API_BASE")
            or get_secret_str("ANTHROPIC_BASE_URL")
        )
        api_key = (
            optional_params.api_key
            or love_engine.api_key
            or love_engine.azure_key
            or get_secret_str("ANTHROPIC_API_KEY")
        )

        response = anthropic_batches_instance.retrieve_batch(
            _is_async=_is_async,
            batch_id=batch_id,
            api_base=api_base,
            api_key=api_key,
            timeout=timeout,
            max_retries=optional_params.max_retries,
        )
    else:
        raise love_engine.exceptions.BadRequestError(
            message=(
                "love_engine doesn't support custom_llm_provider={} for 'retrieve_batch' without a `model` kwarg. "
                "Supported via this path: 'openai', 'azure', 'vertex_ai', 'anthropic'. "
                "'bedrock' is supported but requires `model` to be passed so the provider config can be loaded."
            ).format(custom_llm_provider),
            model="n/a",
            llm_provider=custom_llm_provider,
            response=httpx.Response(
                status_code=400,
                content="Unsupported provider",
                request=httpx.Request(method="retrieve_batch", url="https://github.com/BerriAI/love_engine"),  # type: ignore
            ),
        )
    return response


@client
def retrieve_batch(
    batch_id: str,
    custom_llm_provider: Literal[
        "openai", "azure", "vertex_ai", "bedrock", "hosted_vllm", "anthropic"
    ] = "openai",
    metadata: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Union[LoveEngineBatch, Coroutine[Any, Any, LoveEngineBatch]]:
    """
    Retrieves a batch.

    love_engine Equivalent of GET https://api.openai.com/v1/batches/{batch_id}
    """
    try:
        optional_params = GenericLoveEngineParams(**kwargs)
        love_engine_logging_obj: Optional[LoveEngineLoggingObj] = kwargs.get(
            "love_engine_logging_obj", None
        )
        ### TIMEOUT LOGIC ###
        timeout = optional_params.timeout or kwargs.get("request_timeout", 600) or 600
        love_engine_params = get_love_engine_params(
            custom_llm_provider=custom_llm_provider,
            **kwargs,
        )
        if love_engine_logging_obj is not None:
            love_engine_logging_obj.update_from_kwargs(
                kwargs=kwargs,
                model=None,
                user=None,
                optional_params=optional_params.model_dump(),
                love_engine_params=love_engine_params,
                custom_llm_provider=custom_llm_provider,
            )

        if (
            timeout is not None
            and isinstance(timeout, httpx.Timeout)
            and supports_httpx_timeout(custom_llm_provider) is False
        ):
            read_timeout = timeout.read or 600
            timeout = read_timeout  # default 10 min timeout
        elif timeout is not None and not isinstance(timeout, httpx.Timeout):
            timeout = float(timeout)  # type: ignore
        elif timeout is None:
            timeout = 600.0

        _retrieve_batch_request = RetrieveBatchRequest(
            batch_id=batch_id,
            extra_headers=extra_headers,
            extra_body=extra_body,
        )

        _is_async = kwargs.pop("aretrieve_batch", False) is True
        client = kwargs.get("client", None)

        # Bedrock has two distinct ARN families that need different APIs:
        #   * async-invoke ARNs       (Twelve Labs Marengo embeddings)        -> bedrock-runtime data plane
        #   * model-invocation-job ARNs (CreateModelInvocationJob batch)      -> bedrock control plane
        # They live on different AWS service endpoints and can't share a handler.
        # ARN shapes:
        #   arn:aws(-[^:]+)?:bedrock:<region>:<account>:async-invoke/<id>
        #   arn:aws(-[^:]+)?:bedrock:<region>:<account>:model-invocation-job/<id>
        if batch_id.startswith("arn:aws") and ":bedrock:" in batch_id:
            if ":async-invoke/" in batch_id:
                # Remove aws_region_name from kwargs to avoid duplicate parameter
                async_kwargs = kwargs.copy()
                async_kwargs.pop("aws_region_name", None)

                return BedrockBatchesHandler._handle_async_invoke_status(
                    batch_id=batch_id,
                    aws_region_name=kwargs.get("aws_region_name", "us-east-1"),
                    logging_obj=love_engine_logging_obj,
                    **async_kwargs,
                )
            if ":model-invocation-job/" in batch_id:
                mij_kwargs = kwargs.copy()
                mij_kwargs.pop("aws_region_name", None)

                return BedrockBatchesHandler._handle_model_invocation_job_status(
                    batch_id=batch_id,
                    aws_region_name=kwargs.get("aws_region_name"),
                    logging_obj=love_engine_logging_obj,
                    **mij_kwargs,
                )

        # Try to use provider config first (for providers like bedrock)
        model: Optional[str] = kwargs.get("model", None)
        if model is not None:
            provider_config = ProviderConfigManager.get_provider_batches_config(
                model=model,
                provider=LlmProviders(custom_llm_provider),
            )
        else:
            provider_config = None

        if provider_config is not None:
            response = base_llm_http_handler.retrieve_batch(
                batch_id=batch_id,
                provider_config=provider_config,
                love_engine_params=love_engine_params,
                headers=extra_headers or {},
                api_base=optional_params.api_base,
                api_key=optional_params.api_key,
                logging_obj=love_engine_logging_obj
                or LoveEngineLoggingObj(
                    model=model or f"{custom_llm_provider}/unknown",
                    messages=[],
                    stream=False,
                    call_type="batch_retrieve",
                    start_time=None,
                    love_engine_call_id="batch_retrieve_" + batch_id,
                    function_id="batch_retrieve",
                ),
                _is_async=_is_async,
                client=(
                    client
                    if client is not None
                    and isinstance(client, (HTTPHandler, AsyncHTTPHandler))
                    else None
                ),
                timeout=timeout,
                model=model,
            )
            return response

        #########################################################
        # Handle providers without provider config
        #########################################################
        return _handle_retrieve_batch_providers_without_provider_config(
            batch_id=batch_id,
            custom_llm_provider=custom_llm_provider,
            optional_params=optional_params,
            love_engine_params=love_engine_params,
            _retrieve_batch_request=_retrieve_batch_request,
            _is_async=_is_async,
            timeout=timeout,
            logging_obj=love_engine_logging_obj,
        )

    except Exception as e:
        raise e


@client
async def alist_batches(
    after: Optional[str] = None,
    limit: Optional[int] = None,
    custom_llm_provider: ListBatchesSupportedProvider = "openai",
    metadata: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    **kwargs,
):
    """
    Async: List your organization's batches.
    """

    try:
        loop = asyncio.get_event_loop()
        kwargs["alist_batches"] = True

        # Use a partial function to pass your keyword arguments
        func = partial(
            list_batches,
            after,
            limit,
            custom_llm_provider,
            extra_headers,
            extra_body,
            **kwargs,
        )

        # Add the context to the function
        ctx = contextvars.copy_context()
        func_with_context = partial(ctx.run, func)
        init_response = await loop.run_in_executor(None, func_with_context)
        if asyncio.iscoroutine(init_response):
            response = await init_response
        else:
            response = init_response  # type: ignore

        return response
    except Exception as e:
        raise e


@client
def list_batches(
    after: Optional[str] = None,
    limit: Optional[int] = None,
    custom_llm_provider: ListBatchesSupportedProvider = "openai",
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    **kwargs,
):
    """
    Lists batches

    List your organization's batches.
    """
    try:
        # set API KEY
        optional_params = GenericLoveEngineParams(**kwargs)
        love_engine_params = get_love_engine_params(
            custom_llm_provider=custom_llm_provider,
            **kwargs,
        )
        api_key = (
            optional_params.api_key
            or love_engine.api_key  # for deepinfra/perplexity/anyscale we check in get_llm_provider and pass in the api key from there
            or love_engine.openai_key
            or os.getenv("OPENAI_API_KEY")
        )
        ### TIMEOUT LOGIC ###
        timeout = optional_params.timeout or kwargs.get("request_timeout", 600) or 600
        # set timeout for 10 minutes by default

        if (
            timeout is not None
            and isinstance(timeout, httpx.Timeout)
            and supports_httpx_timeout(custom_llm_provider) is False
        ):
            read_timeout = timeout.read or 600
            timeout = read_timeout  # default 10 min timeout
        elif timeout is not None and not isinstance(timeout, httpx.Timeout):
            timeout = float(timeout)  # type: ignore
        elif timeout is None:
            timeout = 600.0

        _is_async = kwargs.pop("alist_batches", False) is True
        if custom_llm_provider in OPENAI_COMPATIBLE_BATCH_AND_FILES_PROVIDERS:
            # for deepinfra/perplexity/anyscale/groq we check in get_llm_provider and pass in the api base from there
            api_base = (
                optional_params.api_base
                or love_engine.api_base
                or os.getenv("OPENAI_BASE_URL")
                or os.getenv("OPENAI_API_BASE")
                or "https://api.openai.com/v1"
            )
            organization = (
                optional_params.organization
                or love_engine.organization
                or os.getenv("OPENAI_ORGANIZATION", None)
                or None  # default - https://github.com/openai/openai-python/blob/284c1799070c723c6a553337134148a7ab088dd8/openai/util.py#L105
            )

            response = openai_batches_instance.list_batches(
                _is_async=_is_async,
                after=after,
                limit=limit,
                api_base=api_base,
                api_key=api_key,
                organization=organization,
                timeout=timeout,
                max_retries=optional_params.max_retries,
            )
        elif custom_llm_provider == "azure":
            api_base = optional_params.api_base or love_engine.api_base or get_secret_str("AZURE_API_BASE")  # type: ignore
            api_version = (
                optional_params.api_version
                or love_engine.api_version
                or get_secret_str("AZURE_API_VERSION")
            )

            api_key = (
                optional_params.api_key
                or love_engine.api_key
                or love_engine.azure_key
                or get_secret_str("AZURE_OPENAI_API_KEY")
                or get_secret_str("AZURE_API_KEY")
            )

            extra_body = optional_params.get("extra_body", {})
            if extra_body is not None:
                extra_body.pop("azure_ad_token", None)
            else:
                get_secret_str("AZURE_AD_TOKEN")  # type: ignore

            response = azure_batches_instance.list_batches(
                _is_async=_is_async,
                api_base=api_base,
                api_key=api_key,
                api_version=api_version,
                timeout=timeout,
                max_retries=optional_params.max_retries,
                love_engine_params=love_engine_params,
            )
        elif custom_llm_provider == "vertex_ai":
            api_base = optional_params.api_base or ""
            vertex_ai_project = (
                optional_params.vertex_project
                or love_engine.vertex_project
                or get_secret_str("VERTEXAI_PROJECT")
            )
            vertex_ai_location = (
                optional_params.vertex_location
                or love_engine.vertex_location
                or get_secret_str("VERTEXAI_LOCATION")
            )
            vertex_credentials = optional_params.vertex_credentials or get_secret_str(
                "VERTEXAI_CREDENTIALS"
            )

            response = vertex_ai_batches_instance.list_batches(
                _is_async=_is_async,
                after=after,
                limit=limit,
                api_base=api_base,
                vertex_project=vertex_ai_project,
                vertex_location=vertex_ai_location,
                vertex_credentials=vertex_credentials,
                timeout=timeout,
                max_retries=optional_params.max_retries,
            )
        else:
            raise love_engine.exceptions.BadRequestError(
                message="love_engine doesn't support {} for 'list_batch'. Supported providers: {}.".format(
                    custom_llm_provider,
                    ", ".join(sorted(LIST_BATCHES_SUPPORTED_PROVIDERS)),
                ),
                model="n/a",
                llm_provider=custom_llm_provider,
                response=httpx.Response(
                    status_code=400,
                    content="Unsupported provider",
                    request=httpx.Request(method="create_thread", url="https://github.com/BerriAI/love_engine"),  # type: ignore
                ),
            )
        return response
    except Exception as e:
        raise e


async def acancel_batch(
    batch_id: str,
    model: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "vertex_ai"] = "openai",
    metadata: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    **kwargs,
) -> LoveEngineBatch:
    """
    Async: Cancels a batch.

    love_engine Equivalent of POST https://api.openai.com/v1/batches/{batch_id}/cancel
    """
    try:
        loop = asyncio.get_event_loop()
        kwargs["acancel_batch"] = True
        # Preserve model parameter - only pop from kwargs if it exists there
        # (to avoid passing it twice), otherwise keep the function parameter value
        model = kwargs.pop("model", None) or model

        # Use a partial function to pass your keyword arguments
        func = partial(
            cancel_batch,
            batch_id,
            model,
            custom_llm_provider,
            metadata,
            extra_headers,
            extra_body,
            **kwargs,
        )
        # Add the context to the function
        ctx = contextvars.copy_context()
        func_with_context = partial(ctx.run, func)
        init_response = await loop.run_in_executor(None, func_with_context)
        if asyncio.iscoroutine(init_response):
            response = await init_response
        else:
            response = init_response

        return response
    except Exception as e:
        raise e


def cancel_batch(
    batch_id: str,
    model: Optional[str] = None,
    custom_llm_provider: Union[Literal["openai", "azure", "vertex_ai"], str] = "openai",
    metadata: Optional[Dict[str, str]] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, str]] = None,
    **kwargs,
) -> Union[LoveEngineBatch, Coroutine[Any, Any, LoveEngineBatch]]:
    """
    Cancels a batch.

    love_engine Equivalent of POST https://api.openai.com/v1/batches/{batch_id}/cancel
    """
    try:
        try:
            if model is not None:
                _, custom_llm_provider, _, _ = get_llm_provider(
                    model=model,
                    custom_llm_provider=custom_llm_provider,
                )
        except Exception as e:
            verbose_logger.exception(
                f"love_engine.batches.main.py::cancel_batch() - Error inferring custom_llm_provider - {str(e)}"
            )
        optional_params = GenericLoveEngineParams(**kwargs)
        love_engine_params = get_love_engine_params(
            custom_llm_provider=custom_llm_provider,
            **kwargs,
        )
        ### TIMEOUT LOGIC ###
        timeout = optional_params.timeout or kwargs.get("request_timeout", 600) or 600
        # set timeout for 10 minutes by default

        if (
            timeout is not None
            and isinstance(timeout, httpx.Timeout)
            and supports_httpx_timeout(custom_llm_provider) is False
        ):
            read_timeout = timeout.read or 600
            timeout = read_timeout  # default 10 min timeout
        elif timeout is not None and not isinstance(timeout, httpx.Timeout):
            timeout = float(timeout)  # type: ignore
        elif timeout is None:
            timeout = 600.0

        _cancel_batch_request = CancelBatchRequest(
            batch_id=batch_id,
            extra_headers=extra_headers,
            extra_body=extra_body,
        )

        _is_async = kwargs.pop("acancel_batch", False) is True
        api_base: Optional[str] = None
        if custom_llm_provider in OPENAI_COMPATIBLE_BATCH_AND_FILES_PROVIDERS:
            api_base = (
                optional_params.api_base
                or love_engine.api_base
                or os.getenv("OPENAI_BASE_URL")
                or os.getenv("OPENAI_API_BASE")
                or "https://api.openai.com/v1"
            )
            organization = (
                optional_params.organization
                or love_engine.organization
                or os.getenv("OPENAI_ORGANIZATION", None)
                or None
            )
            api_key = (
                optional_params.api_key
                or love_engine.api_key
                or love_engine.openai_key
                or os.getenv("OPENAI_API_KEY")
            )

            response = openai_batches_instance.cancel_batch(
                _is_async=_is_async,
                cancel_batch_data=_cancel_batch_request,
                api_base=api_base,
                api_key=api_key,
                organization=organization,
                timeout=timeout,
                max_retries=optional_params.max_retries,
            )
        elif custom_llm_provider == "azure":
            api_base = (
                optional_params.api_base
                or love_engine.api_base
                or get_secret_str("AZURE_API_BASE")
            )
            api_version = (
                optional_params.api_version
                or love_engine.api_version
                or get_secret_str("AZURE_API_VERSION")
            )

            api_key = (
                optional_params.api_key
                or love_engine.api_key
                or love_engine.azure_key
                or get_secret_str("AZURE_OPENAI_API_KEY")
                or get_secret_str("AZURE_API_KEY")
            )

            extra_body = optional_params.get("extra_body", {})
            if extra_body is not None:
                extra_body.pop("azure_ad_token", None)
            else:
                get_secret_str("AZURE_AD_TOKEN")  # type: ignore

            response = azure_batches_instance.cancel_batch(
                _is_async=_is_async,
                api_base=api_base,
                api_key=api_key,
                api_version=api_version,
                timeout=timeout,
                max_retries=optional_params.max_retries,
                cancel_batch_data=_cancel_batch_request,
                love_engine_params=love_engine_params,
            )
        elif custom_llm_provider == "vertex_ai":
            api_base = optional_params.api_base or None
            vertex_ai_project = (
                optional_params.vertex_project
                or love_engine.vertex_project
                or get_secret_str("VERTEXAI_PROJECT")
            )
            vertex_ai_location = (
                optional_params.vertex_location
                or love_engine.vertex_location
                or get_secret_str("VERTEXAI_LOCATION")
            )
            vertex_credentials = optional_params.vertex_credentials or get_secret_str(
                "VERTEXAI_CREDENTIALS"
            )

            response = vertex_ai_batches_instance.cancel_batch(
                _is_async=_is_async,
                batch_id=batch_id,
                api_base=api_base,
                vertex_project=vertex_ai_project,
                vertex_location=vertex_ai_location,
                vertex_credentials=vertex_credentials,
                timeout=timeout,
                max_retries=optional_params.max_retries,
            )
        else:
            raise love_engine.exceptions.BadRequestError(
                message="love_engine doesn't support {} for 'cancel_batch'. Only 'openai', 'azure', and 'vertex_ai' are supported.".format(
                    custom_llm_provider
                ),
                model="n/a",
                llm_provider=custom_llm_provider,
                response=httpx.Response(
                    status_code=400,
                    content="Unsupported provider",
                    request=httpx.Request(method="cancel_batch", url="https://github.com/BerriAI/love_engine"),  # type: ignore
                ),
            )
        return response
    except Exception as e:
        raise e


def _handle_async_invoke_status(
    batch_id: str, aws_region_name: str, logging_obj=None, **kwargs
) -> "LoveEngineBatch":
    """
    Handle async invoke status check for AWS Bedrock.

    Args:
        batch_id: The async invoke ARN
        aws_region_name: AWS region name
        **kwargs: Additional parameters

    Returns:
        dict: Status information including status, output_file_id (S3 URL), etc.
    """
    import asyncio

    from love_engine.llms.bedrock.embed.embedding import BedrockEmbedding

    async def _async_get_status():
        # Create embedding handler instance
        embedding_handler = BedrockEmbedding()

        # Get the status of the async invoke job
        status_response = await embedding_handler._get_async_invoke_status(
            invocation_arn=batch_id,
            aws_region_name=aws_region_name,
            logging_obj=logging_obj,
            **kwargs,
        )

        # Transform response to a LoveEngineBatch object
        from love_engine.types.llms.openai import BatchJobStatus
        from love_engine.types.utils import LoveEngineBatch

        # Normalize status to lowercase (AWS returns 'Completed', 'Failed', etc.)
        aws_status_raw = status_response.get("status", "")
        aws_status_lower = aws_status_raw.lower()
        # Map AWS status values to love_engine expected values
        status_mapping: dict[str, BatchJobStatus] = {
            "completed": "completed",
            "failed": "failed",
            "inprogress": "in_progress",
            "in_progress": "in_progress",
        }
        normalized_status: BatchJobStatus = status_mapping.get(
            aws_status_lower, "failed"
        )  # Default to "failed" if unknown status

        # Get output S3 URI safely
        output_s3_uri = ""
        try:
            output_s3_uri = status_response["outputDataConfig"]["s3OutputDataConfig"][
                "s3Uri"
            ]
        except (KeyError, TypeError):
            pass

        # Use BedrockBatchesConfig's timestamp parsing method (expects raw AWS status string)
        import time

        from love_engine.llms.bedrock.batches.transformation import BedrockBatchesConfig

        (
            created_at,
            in_progress_at,
            completed_at,
            failed_at,
            _,
            _,
        ) = BedrockBatchesConfig()._parse_timestamps_and_status(
            status_response, aws_status_raw
        )
        result = LoveEngineBatch(
            id=status_response["invocationArn"],
            object="batch",
            status=normalized_status,
            created_at=created_at
            or int(time.time()),  # Provide default timestamp if None
            in_progress_at=in_progress_at,
            completed_at=completed_at,
            failed_at=failed_at,
            request_counts=BatchRequestCounts(
                total=1,
                completed=1 if normalized_status == "completed" else 0,
                failed=1 if normalized_status == "failed" else 0,
            ),
            metadata=dict(
                **{
                    "output_file_id": output_s3_uri,
                    "failure_message": status_response.get("failureMessage") or "",
                    "model_arn": status_response["modelArn"],
                }
            ),
            completion_window="24h",
            endpoint="/v1/embeddings",
            input_file_id="",
        )

        return result

    # Since this function is called from within an async context via run_in_executor,
    # we need to create a new event loop in a thread to avoid conflicts
    import concurrent.futures

    def run_in_thread():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(_async_get_status())
        finally:
            new_loop.close()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result()
