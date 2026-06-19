"""
Main entry point for Skills API operations
Provides create, list, get, and delete operations for skills
"""

import asyncio
import contextvars
from functools import partial
from typing import Any, Coroutine, Dict, List, Optional, Union

import httpx

import love_engine
from love_engine.constants import request_timeout
from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
from love_engine.llms.base_llm.skills.transformation import BaseSkillsAPIConfig
from love_engine.llms.custom_httpx.llm_http_handler import BaseLLMHTTPHandler
from love_engine.types.llms.anthropic_skills import (
    CreateSkillRequest,
    DeleteSkillResponse,
    ListSkillsParams,
    ListSkillsResponse,
    Skill,
)
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import LlmProviders
from love_engine.utils import ProviderConfigManager, client

# Initialize HTTP handler
base_llm_http_handler = BaseLLMHTTPHandler()
DEFAULT_ANTHROPIC_API_BASE = "https://api.anthropic.com/v1"

# Initialize LoveEngine skills handler (lazy - only used when custom_llm_provider="love_engine")
_love_engine_skills_handler = None


def _get_user_api_key_auth_from_kwargs(kwargs: Dict[str, Any]) -> Optional[Any]:
    for metadata_key in ("metadata", "love_engine_metadata"):
        metadata = kwargs.get(metadata_key)
        if isinstance(metadata, dict) and metadata.get("user_api_key_auth") is not None:
            return metadata["user_api_key_auth"]
    return None


def _get_skill_request_metadata(
    kwargs: Dict[str, Any],
    extra_body: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if extra_body and isinstance(extra_body.get("metadata"), dict):
        return extra_body["metadata"]

    metadata = kwargs.get("metadata")
    if isinstance(metadata, dict) and isinstance(
        metadata.get("requester_metadata"), dict
    ):
        return metadata["requester_metadata"]
    return None


def _get_love_engine_skills_handler():
    """Lazy initialization of LoveEngine skills handler to avoid import overhead."""
    global _love_engine_skills_handler
    if _love_engine_skills_handler is None:
        from love_engine.llms.love_engine_proxy.skills.transformation import (
            LoveEngineSkillsTransformationHandler,
        )

        _love_engine_skills_handler = LoveEngineSkillsTransformationHandler()
    return _love_engine_skills_handler


@client
async def acreate_skill(
    files: Optional[List[Any]] = None,
    display_title: Optional[str] = None,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> Skill:
    """
    Async: Create a new skill

    Args:
        files: Files to upload for the skill. All files must be in the same top-level directory and must include a SKILL.md file at the root.
        display_title: Optional display title for the skill
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        extra_body: Additional body parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        Skill object
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["acreate_skill"] = True

        func = partial(
            create_skill,
            files=files,
            display_title=display_title,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
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
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


@client
def create_skill(
    files: Optional[List[Any]] = None,
    display_title: Optional[str] = None,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> Union[Skill, Coroutine[Any, Any, Skill]]:
    """
    Create a new skill

    Args:
        files: Files to upload for the skill. All files must be in the same top-level directory and must include a SKILL.md file at the root.
        display_title: Optional display title for the skill
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        extra_body: Additional body parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        Skill object
    """
    local_vars = locals()
    try:
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.get("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id", None)
        _is_async = kwargs.pop("acreate_skill", False) is True

        # Get LoveEngine parameters
        love_engine_params = GenericLoveEngineParams(**kwargs)

        # Determine provider
        if custom_llm_provider is None:
            custom_llm_provider = "anthropic"

        # Build create request
        create_request: CreateSkillRequest = {}
        if display_title is not None:
            create_request["display_title"] = display_title
        if files is not None:
            create_request["files"] = files

        # Merge extra_body if provided
        if extra_body:
            create_request.update(extra_body)  # type: ignore

        # Route to LoveEngine DB if custom_llm_provider="love_engine_proxy"
        if custom_llm_provider == LlmProviders.LOVE_ENGINE_PROXY.value:
            return _get_love_engine_skills_handler().create_skill_handler(
                display_title=display_title,
                files=files,
                metadata=_get_skill_request_metadata(kwargs, extra_body),
                user_id=kwargs.get("user_id"),
                user_api_key_dict=_get_user_api_key_auth_from_kwargs(kwargs),
                _is_async=_is_async,
                logging_obj=love_engine_logging_obj,
                love_engine_call_id=love_engine_call_id,
            )

        # Get provider config for external providers (Anthropic, etc.)
        skills_api_provider_config: Optional[BaseSkillsAPIConfig] = (
            ProviderConfigManager.get_provider_skills_api_config(
                provider=love_engine.LlmProviders(custom_llm_provider),
            )
        )

        if skills_api_provider_config is None:
            raise ValueError(f"CREATE skill is not supported for {custom_llm_provider}")

        # Validate environment and get headers
        headers = extra_headers or {}
        headers = skills_api_provider_config.validate_environment(
            headers=headers, love_engine_params=love_engine_params
        )

        # Transform request
        request_body = skills_api_provider_config.transform_create_skill_request(
            create_request=create_request,
            love_engine_params=love_engine_params,
            headers=headers,
        )

        # Get API base and URL
        from love_engine.llms.anthropic.common_utils import AnthropicModelInfo

        api_base = AnthropicModelInfo.get_api_base(love_engine_params.api_base)
        url = skills_api_provider_config.get_complete_url(
            api_base=api_base, endpoint="skills"
        )

        # Pre-call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model=None,
            optional_params=request_body,
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=custom_llm_provider,
        )

        # Make HTTP request
        response = base_llm_http_handler.create_skill_handler(
            url=url,
            request_body=request_body,
            skills_api_provider_config=skills_api_provider_config,
            custom_llm_provider=custom_llm_provider,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=headers,
            timeout=timeout or request_timeout,
            _is_async=_is_async,
            client=kwargs.get("client"),
            shared_session=kwargs.get("shared_session"),
        )

        return response
    except Exception as e:
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


@client
async def alist_skills(
    limit: Optional[int] = None,
    page: Optional[str] = None,
    source: Optional[str] = None,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> ListSkillsResponse:
    """
    Async: List all skills

    Args:
        limit: Number of results to return per page (max 100, default 20)
        page: Pagination token for fetching a specific page of results
        source: Filter skills by source ('custom' or 'anthropic')
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        ListSkillsResponse object
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["alist_skills"] = True

        func = partial(
            list_skills,
            limit=limit,
            page=page,
            source=source,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
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
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


@client
def list_skills(
    limit: Optional[int] = None,
    page: Optional[str] = None,
    source: Optional[str] = None,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> Union[ListSkillsResponse, Coroutine[Any, Any, ListSkillsResponse]]:
    """
    List all skills

    Args:
        limit: Number of results to return per page (max 100, default 20)
        page: Pagination token for fetching a specific page of results
        source: Filter skills by source ('custom' or 'anthropic')
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        ListSkillsResponse object
    """
    local_vars = locals()
    try:
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.get("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id", None)
        _is_async = kwargs.pop("alist_skills", False) is True

        # Get LoveEngine parameters
        love_engine_params = GenericLoveEngineParams(**kwargs)

        # Determine provider
        if custom_llm_provider is None:
            custom_llm_provider = "anthropic"

        # Route to LoveEngine DB if custom_llm_provider="love_engine_proxy"
        if custom_llm_provider == LlmProviders.LOVE_ENGINE_PROXY.value:
            return _get_love_engine_skills_handler().list_skills_handler(
                limit=limit or 20,
                offset=0,
                user_api_key_dict=_get_user_api_key_auth_from_kwargs(kwargs),
                _is_async=_is_async,
                logging_obj=love_engine_logging_obj,
                love_engine_call_id=love_engine_call_id,
            )

        # Get provider config for external providers (Anthropic, etc.)
        skills_api_provider_config: Optional[BaseSkillsAPIConfig] = (
            ProviderConfigManager.get_provider_skills_api_config(
                provider=love_engine.LlmProviders(custom_llm_provider),
            )
        )

        if skills_api_provider_config is None:
            raise ValueError(f"LIST skills is not supported for {custom_llm_provider}")

        # Build list parameters
        list_params: ListSkillsParams = {}
        if limit is not None:
            list_params["limit"] = limit
        if page is not None:
            list_params["page"] = page
        if source is not None:
            list_params["source"] = source

        # Merge extra_query if provided
        if extra_query:
            list_params.update(extra_query)  # type: ignore

        # Validate environment and get headers
        headers = extra_headers or {}
        headers = skills_api_provider_config.validate_environment(
            headers=headers, love_engine_params=love_engine_params
        )

        # Transform request
        url, query_params = skills_api_provider_config.transform_list_skills_request(
            list_params=list_params,
            love_engine_params=love_engine_params,
            headers=headers,
        )

        # Pre-call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model=None,
            optional_params=query_params,
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=custom_llm_provider,
        )

        # Make HTTP request
        response = base_llm_http_handler.list_skills_handler(
            url=url,
            query_params=query_params,
            skills_api_provider_config=skills_api_provider_config,
            custom_llm_provider=custom_llm_provider,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=headers,
            timeout=timeout or request_timeout,
            _is_async=_is_async,
            client=kwargs.get("client"),
            shared_session=kwargs.get("shared_session"),
        )

        return response
    except Exception as e:
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


@client
async def aget_skill(
    skill_id: str,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> Skill:
    """
    Async: Get a skill by ID

    Args:
        skill_id: The ID of the skill to fetch
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        Skill object
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["aget_skill"] = True

        func = partial(
            get_skill,
            skill_id=skill_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
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
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


@client
def get_skill(
    skill_id: str,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> Union[Skill, Coroutine[Any, Any, Skill]]:
    """
    Get a skill by ID

    Args:
        skill_id: The ID of the skill to fetch
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        Skill object
    """
    local_vars = locals()
    try:
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.get("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id", None)
        _is_async = kwargs.pop("aget_skill", False) is True

        # Get LoveEngine parameters
        love_engine_params = GenericLoveEngineParams(**kwargs)

        # Determine provider
        if custom_llm_provider is None:
            custom_llm_provider = "anthropic"

        # Route to LoveEngine DB if custom_llm_provider="love_engine_proxy"
        if custom_llm_provider == LlmProviders.LOVE_ENGINE_PROXY.value:
            return _get_love_engine_skills_handler().get_skill_handler(
                skill_id=skill_id,
                user_api_key_dict=_get_user_api_key_auth_from_kwargs(kwargs),
                _is_async=_is_async,
                logging_obj=love_engine_logging_obj,
                love_engine_call_id=love_engine_call_id,
            )

        # Get provider config for external providers (Anthropic, etc.)
        skills_api_provider_config: Optional[BaseSkillsAPIConfig] = (
            ProviderConfigManager.get_provider_skills_api_config(
                provider=love_engine.LlmProviders(custom_llm_provider),
            )
        )

        if skills_api_provider_config is None:
            raise ValueError(f"GET skill is not supported for {custom_llm_provider}")

        # Validate environment and get headers
        headers = extra_headers or {}
        headers = skills_api_provider_config.validate_environment(
            headers=headers, love_engine_params=love_engine_params
        )

        # Get API base
        from love_engine.llms.anthropic.common_utils import AnthropicModelInfo

        api_base = AnthropicModelInfo.get_api_base(love_engine_params.api_base)

        # Transform request
        url, headers = skills_api_provider_config.transform_get_skill_request(
            skill_id=skill_id,
            api_base=api_base or DEFAULT_ANTHROPIC_API_BASE,
            love_engine_params=love_engine_params,
            headers=headers,
        )

        # Pre-call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model=None,
            optional_params={"skill_id": skill_id},
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=custom_llm_provider,
        )

        # Make HTTP request
        response = base_llm_http_handler.get_skill_handler(
            url=url,
            skills_api_provider_config=skills_api_provider_config,
            custom_llm_provider=custom_llm_provider,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=headers,
            timeout=timeout or request_timeout,
            _is_async=_is_async,
            client=kwargs.get("client"),
            shared_session=kwargs.get("shared_session"),
        )

        return response
    except Exception as e:
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


@client
async def adelete_skill(
    skill_id: str,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> DeleteSkillResponse:
    """
    Async: Delete a skill by ID

    Args:
        skill_id: The ID of the skill to delete
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        DeleteSkillResponse object
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["adelete_skill"] = True

        func = partial(
            delete_skill,
            skill_id=skill_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
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
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


@client
def delete_skill(
    skill_id: str,
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    timeout: Optional[Union[float, httpx.Timeout]] = None,
    custom_llm_provider: Optional[str] = None,
    **kwargs,
) -> Union[DeleteSkillResponse, Coroutine[Any, Any, DeleteSkillResponse]]:
    """
    Delete a skill by ID

    Args:
        skill_id: The ID of the skill to delete
        extra_headers: Additional headers for the request
        extra_query: Additional query parameters
        timeout: Request timeout
        custom_llm_provider: Provider name (e.g., 'anthropic')
        **kwargs: Additional parameters

    Returns:
        DeleteSkillResponse object
    """
    local_vars = locals()
    try:
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.get("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id", None)
        _is_async = kwargs.pop("adelete_skill", False) is True

        # Get LoveEngine parameters
        love_engine_params = GenericLoveEngineParams(**kwargs)

        # Determine provider
        if custom_llm_provider is None:
            custom_llm_provider = "anthropic"

        # Route to LoveEngine DB if custom_llm_provider="love_engine_proxy"
        if custom_llm_provider == LlmProviders.LOVE_ENGINE_PROXY.value:
            return _get_love_engine_skills_handler().delete_skill_handler(
                skill_id=skill_id,
                user_api_key_dict=_get_user_api_key_auth_from_kwargs(kwargs),
                _is_async=_is_async,
                logging_obj=love_engine_logging_obj,
                love_engine_call_id=love_engine_call_id,
            )

        # Get provider config for external providers (Anthropic, etc.)
        skills_api_provider_config: Optional[BaseSkillsAPIConfig] = (
            ProviderConfigManager.get_provider_skills_api_config(
                provider=love_engine.LlmProviders(custom_llm_provider),
            )
        )

        if skills_api_provider_config is None:
            raise ValueError(f"DELETE skill is not supported for {custom_llm_provider}")

        # Validate environment and get headers
        headers = extra_headers or {}
        headers = skills_api_provider_config.validate_environment(
            headers=headers, love_engine_params=love_engine_params
        )

        # Get API base
        from love_engine.llms.anthropic.common_utils import AnthropicModelInfo

        api_base = AnthropicModelInfo.get_api_base(love_engine_params.api_base)

        # Transform request
        url, headers = skills_api_provider_config.transform_delete_skill_request(
            skill_id=skill_id,
            api_base=api_base or DEFAULT_ANTHROPIC_API_BASE,
            love_engine_params=love_engine_params,
            headers=headers,
        )

        # Pre-call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model=None,
            optional_params={"skill_id": skill_id},
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=custom_llm_provider,
        )

        # Make HTTP request
        response = base_llm_http_handler.delete_skill_handler(
            url=url,
            skills_api_provider_config=skills_api_provider_config,
            custom_llm_provider=custom_llm_provider,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=headers,
            timeout=timeout or request_timeout,
            _is_async=_is_async,
            client=kwargs.get("client"),
            shared_session=kwargs.get("shared_session"),
        )

        return response
    except Exception as e:
        raise love_engine.exception_type(
            model=None,
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )
