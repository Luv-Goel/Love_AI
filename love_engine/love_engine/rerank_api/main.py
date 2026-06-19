import asyncio
import contextvars
from functools import partial
from typing import Any, Coroutine, Dict, List, Literal, Optional, Union

import love_engine
from love_engine._logging import verbose_logger
from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
from love_engine.llms.base_llm.rerank.transformation import BaseRerankConfig
from love_engine.llms.bedrock.rerank.handler import BedrockRerankHandler
from love_engine.llms.custom_httpx.llm_http_handler import BaseLLMHTTPHandler
from love_engine.llms.together_ai.rerank.handler import TogetherAIRerank
from love_engine.llms.watsonx.common_utils import IBMWatsonXMixin
from love_engine.rerank_api.rerank_utils import get_optional_rerank_params
from love_engine.secret_managers.main import get_secret, get_secret_str
from love_engine.types.rerank import RerankResponse
from love_engine.types.router import *
from love_engine.utils import ProviderConfigManager, client, exception_type

####### ENVIRONMENT VARIABLES ###################
# Initialize any necessary instances or variables here
together_rerank = TogetherAIRerank()
bedrock_rerank = BedrockRerankHandler()
base_llm_http_handler = BaseLLMHTTPHandler()
#################################################


@client
async def arerank(
    model: str,
    query: str,
    documents: List[Union[str, Dict[str, Any]]],
    custom_llm_provider: Optional[
        Literal[
            "cohere", "together_ai", "deepinfra", "fireworks_ai", "voyage", "watsonx"
        ]
    ] = None,
    top_n: Optional[int] = None,
    rank_fields: Optional[List[str]] = None,
    return_documents: Optional[bool] = None,
    max_chunks_per_doc: Optional[int] = None,
    **kwargs,
) -> Union[RerankResponse, Coroutine[Any, Any, RerankResponse]]:
    """
    Async: Reranks a list of documents based on their relevance to the query
    """
    try:
        loop = asyncio.get_event_loop()
        kwargs["arerank"] = True

        func = partial(
            rerank,
            model,
            query,
            documents,
            custom_llm_provider,
            top_n,
            rank_fields,
            return_documents,
            max_chunks_per_doc,
            **kwargs,
        )

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
def rerank(
    model: str,
    query: str,
    documents: List[Union[str, Dict[str, Any]]],
    custom_llm_provider: Optional[
        Literal[
            "cohere",
            "together_ai",
            "azure_ai",
            "infinity",
            "love_engine_proxy",
            "hosted_vllm",
            "deepinfra",
            "fireworks_ai",
            "voyage",
            "watsonx",
        ]
    ] = None,
    top_n: Optional[int] = None,
    rank_fields: Optional[List[str]] = None,
    return_documents: Optional[bool] = True,
    max_chunks_per_doc: Optional[int] = None,
    max_tokens_per_doc: Optional[int] = None,
    **kwargs,
) -> Union[RerankResponse, Coroutine[Any, Any, RerankResponse]]:
    """
    Reranks a list of documents based on their relevance to the query
    """
    headers: Optional[dict] = kwargs.get("headers")  # type: ignore
    love_engine_logging_obj: LoveEngineLoggingObj = kwargs.get("love_engine_logging_obj")  # type: ignore
    love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id", None)
    proxy_server_request = kwargs.get("proxy_server_request", None)
    model_info = kwargs.get("model_info", None)
    user = kwargs.get("user", None)
    client = kwargs.get("client", None)
    try:
        _is_async = kwargs.pop("arerank", False) is True
        optional_params = GenericLoveEngineParams(**kwargs)
        # Params that are unique to specific versions of the client for the rerank call
        unique_version_params = {
            "max_chunks_per_doc": max_chunks_per_doc,
            "max_tokens_per_doc": max_tokens_per_doc,
        }
        present_version_params = [
            k for k, v in unique_version_params.items() if v is not None
        ]

        (
            model,
            _custom_llm_provider,
            dynamic_api_key,
            dynamic_api_base,
        ) = love_engine.get_llm_provider(
            model=model,
            custom_llm_provider=custom_llm_provider,
            api_base=optional_params.api_base,
            api_key=optional_params.api_key,
        )

        rerank_provider_config: BaseRerankConfig = (
            ProviderConfigManager.get_provider_rerank_config(
                model=model,
                provider=love_engine.LlmProviders(_custom_llm_provider),
                api_base=optional_params.api_base,
                present_version_params=present_version_params,
            )
        )

        optional_rerank_params: Dict = get_optional_rerank_params(
            rerank_provider_config=rerank_provider_config,
            model=model,
            drop_params=kwargs.get("drop_params") or love_engine.drop_params or False,
            query=query,
            documents=documents,
            custom_llm_provider=_custom_llm_provider,
            top_n=top_n,
            rank_fields=rank_fields,
            return_documents=return_documents,
            max_chunks_per_doc=max_chunks_per_doc,
            max_tokens_per_doc=max_tokens_per_doc,
            non_default_params=kwargs,
        )
        verbose_logger.info(f"optional_rerank_params: {optional_rerank_params}")
        if isinstance(optional_params.timeout, str):
            optional_params.timeout = float(optional_params.timeout)

        model_response = RerankResponse()

        rerank_love_engine_params = {
            "love_engine_call_id": love_engine_call_id,
            "proxy_server_request": proxy_server_request,
            "model_info": model_info,
            "preset_cache_key": None,
            "stream_response": {},
            **optional_params.model_dump(exclude_unset=True),
        }

        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model=model,
            user=user,
            optional_params=dict(optional_rerank_params),
            love_engine_params=dict(rerank_love_engine_params),
            custom_llm_provider=_custom_llm_provider,
        )

        # Implement rerank logic here based on the custom_llm_provider
        if (
            _custom_llm_provider == love_engine.LlmProviders.COHERE
            or _custom_llm_provider == love_engine.LlmProviders.LOVE_ENGINE_PROXY
        ):
            # Implement Cohere rerank logic
            api_key: Optional[str] = (
                dynamic_api_key or optional_params.api_key or love_engine.api_key
            )

            api_base: Optional[str] = (
                dynamic_api_base
                or optional_params.api_base
                or love_engine.api_base
                or get_secret("COHERE_API_BASE")  # type: ignore
                or "https://api.cohere.com"
            )

            if api_base is None:
                raise Exception(
                    "Invalid api base. api_base=None. Set in call or via `COHERE_API_BASE` env var."
                )
            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.AZURE_AI:
            api_base = (
                dynamic_api_base  # for deepinfra/perplexity/anyscale/groq/friendliai we check in get_llm_provider and pass in the api base from there
                or optional_params.api_base
                or love_engine.api_base
                or get_secret("AZURE_AI_API_BASE")  # type: ignore
            )
            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                optional_rerank_params=optional_rerank_params,
                provider_config=rerank_provider_config,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=dynamic_api_key or optional_params.api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.INFINITY:
            # Implement Infinity rerank logic
            api_key = dynamic_api_key or optional_params.api_key or love_engine.api_key

            api_base = (
                dynamic_api_base
                or optional_params.api_base
                or love_engine.api_base
                or get_secret_str("INFINITY_API_BASE")
            )

            if api_base is None:
                raise Exception(
                    "Invalid api base. api_base=None. Set in call or via `INFINITY_API_BASE` env var."
                )

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=dynamic_api_key or optional_params.api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.TOGETHER_AI:
            # Implement Together AI rerank logic
            api_key = (
                dynamic_api_key
                or optional_params.api_key
                or love_engine.togetherai_api_key
                or get_secret("TOGETHERAI_API_KEY")  # type: ignore
                or love_engine.api_key
            )

            if api_key is None:
                raise ValueError(
                    "TogetherAI API key is required, please set 'TOGETHERAI_API_KEY' in your environment"
                )

            response = together_rerank.rerank(
                model=model,
                query=query,
                documents=documents,
                top_n=top_n,
                rank_fields=rank_fields,
                return_documents=return_documents,
                max_chunks_per_doc=max_chunks_per_doc,
                api_key=api_key,
                _is_async=_is_async,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.JINA_AI:
            if dynamic_api_key is None:
                raise ValueError(
                    "Jina AI API key is required, please set 'JINA_AI_API_KEY' in your environment"
                )

            api_base = (
                dynamic_api_base
                or optional_params.api_base
                or love_engine.api_base
                or get_secret("BEDROCK_API_BASE")  # type: ignore
            )

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                provider_config=rerank_provider_config,
                timeout=optional_params.timeout,
                api_key=dynamic_api_key or optional_params.api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.NVIDIA_NIM:
            if dynamic_api_key is None:
                raise ValueError(
                    "Nvidia NIM API key is required, please set 'NVIDIA_NIM_API_KEY' in your environment"
                )

            # Note: For rerank, the base URL is different from chat/embeddings
            # Rerank uses ai.api.nvidia.com instead of integrate.api.nvidia.com
            api_base = (
                optional_params.api_base
                or get_secret("NVIDIA_NIM_API_BASE")  # type: ignore
                or "https://ai.api.nvidia.com"  # Default for rerank
            )

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                provider_config=rerank_provider_config,
                timeout=optional_params.timeout,
                api_key=dynamic_api_key or optional_params.api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.BEDROCK:
            api_base = (
                dynamic_api_base
                or optional_params.api_base
                or love_engine.api_base
                or get_secret("BEDROCK_API_BASE")  # type: ignore
            )

            # Merge headers and extra_headers if both are provided
            merged_headers = headers or love_engine.headers or {}
            extra_headers_from_kwargs = kwargs.get("extra_headers")
            if extra_headers_from_kwargs:
                merged_headers = {**merged_headers, **extra_headers_from_kwargs}

            response = bedrock_rerank.rerank(
                model=model,
                query=query,
                documents=documents,
                top_n=top_n,
                rank_fields=rank_fields,
                return_documents=return_documents,
                max_chunks_per_doc=max_chunks_per_doc,
                _is_async=_is_async,
                optional_params=optional_params.model_dump(exclude_unset=True),
                timeout=optional_params.timeout,
                api_base=api_base,
                extra_headers=merged_headers,
                logging_obj=love_engine_logging_obj,
                client=client,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.HOSTED_VLLM:
            # Implement Hosted VLLM rerank logic
            api_key = (
                dynamic_api_key
                or optional_params.api_key
                or get_secret_str("HOSTED_VLLM_API_KEY")
            )

            api_base = (
                dynamic_api_base
                or optional_params.api_base
                or get_secret_str("HOSTED_VLLM_API_BASE")
            )

            if api_base is None:
                raise ValueError(
                    "api_base must be provided for Hosted VLLM rerank. Set in call or via HOSTED_VLLM_API_BASE env var."
                )

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )

        elif _custom_llm_provider == love_engine.LlmProviders.DEEPINFRA:
            api_key = (
                dynamic_api_key
                or optional_params.api_key
                or get_secret_str("DEEPINFRA_API_KEY")
            )

            api_base = (
                dynamic_api_base
                or optional_params.api_base
                or get_secret_str("DEEPINFRA_API_BASE")
            )

            if api_base is None:
                raise ValueError(
                    "api_base must be provided for Deepinfra rerank. Set in call or via DEEPINFRA_API_BASE env var."
                )

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.FIREWORKS_AI:
            api_key = (
                dynamic_api_key
                or optional_params.api_key
                or get_secret_str("FIREWORKS_API_KEY")
                or get_secret_str("FIREWORKS_AI_API_KEY")
                or get_secret_str("FIREWORKSAI_API_KEY")
                or get_secret_str("FIREWORKS_AI_TOKEN")
            )

            api_base = (
                dynamic_api_base
                or optional_params.api_base
                or get_secret_str("FIREWORKS_AI_API_BASE")
            )

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.VOYAGE:
            api_key = (
                dynamic_api_key
                or optional_params.api_key
                or get_secret_str("VOYAGE_API_KEY")
                or get_secret_str("VOYAGE_AI_API_KEY")
            )

            api_base = (
                dynamic_api_base
                or optional_params.api_base
                or get_secret_str("VOYAGE_API_BASE")
            )

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        elif _custom_llm_provider == love_engine.LlmProviders.WATSONX:
            credentials = IBMWatsonXMixin.get_watsonx_credentials(
                optional_params=dict(optional_params),
                api_key=dynamic_api_key,
                api_base=dynamic_api_base,
            )

            api_key = credentials["api_key"]
            api_base = credentials["api_base"]

            if credentials.get("token") is not None:
                optional_rerank_params["token"] = credentials["token"]

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=api_key,
                api_base=api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )
        else:
            # Generic handler for all providers that use base_llm_http_handler
            # Provider-specific logic (API key validation, URL generation, etc.)
            # is handled in the respective transformation configs

            # Check if the provider is actually supported
            # If rerank_provider_config is a default CohereRerankConfig but the provider is not Cohere or love_engine_proxy,
            # it means the provider is not supported
            if (
                (
                    isinstance(rerank_provider_config, love_engine.CohereRerankConfig)
                    or isinstance(rerank_provider_config, love_engine.CohereRerankV2Config)
                )
                and _custom_llm_provider != "cohere"
                and _custom_llm_provider != "love_engine_proxy"
            ):
                raise ValueError(f"Unsupported provider: {_custom_llm_provider}")

            response = base_llm_http_handler.rerank(
                model=model,
                custom_llm_provider=_custom_llm_provider,
                provider_config=rerank_provider_config,
                optional_rerank_params=optional_rerank_params,
                logging_obj=love_engine_logging_obj,
                timeout=optional_params.timeout,
                api_key=dynamic_api_key or optional_params.api_key,
                api_base=dynamic_api_base or optional_params.api_base,
                _is_async=_is_async,
                headers=headers or love_engine.headers or {},
                client=client,
                model_response=model_response,
                love_engine_params=rerank_love_engine_params,
            )

        # Placeholder return
        return response
    except Exception as e:
        verbose_logger.error(f"Error in rerank: {str(e)}")
        raise exception_type(
            model=model, custom_llm_provider=custom_llm_provider, original_exception=e
        )
