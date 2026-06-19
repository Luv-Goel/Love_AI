import asyncio
import contextvars
import json
from functools import partial
from typing import Any, Coroutine, Dict, List, Literal, Optional, Union, overload

import love_engine
from love_engine.constants import request_timeout as DEFAULT_REQUEST_TIMEOUT
from love_engine.containers.utils import (
    ContainerRequestUtils,
    decode_managed_container_id_for_request,
)
from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
from love_engine.llms.base_llm.containers.transformation import BaseContainerConfig
from love_engine.main import base_llm_http_handler
from love_engine.types.containers.main import (
    ContainerCreateOptionalRequestParams,
    ContainerFileListResponse,
    ContainerFileObject,
    ContainerListOptionalRequestParams,
    ContainerListResponse,
    ContainerObject,
    DeleteContainerResult,
)
from love_engine.types.llms.openai import FileTypes
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import CallTypes
from love_engine.utils import ProviderConfigManager, client

__all__ = [
    "acreate_container",
    "adelete_container",
    "alist_container_files",
    "alist_containers",
    "aretrieve_container",
    "aupload_container_file",
    "create_container",
    "delete_container",
    "list_container_files",
    "list_containers",
    "retrieve_container",
    "upload_container_file",
]


##### Container Create #######################
@client
async def acreate_container(
    name: str,
    expires_after: Optional[Dict[str, Any]] = None,
    file_ids: Optional[List[str]] = None,
    timeout=600,  # default to 10 minutes
    # love_engine specific params,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> ContainerObject:
    """Asynchronously calls the `create_container` function with the given arguments and keyword arguments.

    Parameters:
    - `name` (str): Name of the container to create
    - `expires_after` (Optional[Dict[str, Any]]): Container expiration time settings
    - `file_ids` (Optional[List[str]]): IDs of files to copy to the container
    - `timeout` (int): Request timeout in seconds
    - `custom_llm_provider` (Optional[Literal["openai"]]): The LLM provider to use
    - `extra_headers` (Optional[Dict[str, Any]]): Additional headers
    - `extra_query` (Optional[Dict[str, Any]]): Additional query parameters
    - `extra_body` (Optional[Dict[str, Any]]): Additional body parameters
    - `kwargs` (dict): Additional keyword arguments

    Returns:
    - `response` (ContainerObject): The created container object
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["async_call"] = True

        func = partial(
            create_container,
            name=name,
            expires_after=expires_after,
            file_ids=file_ids,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
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
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


# fmt: off

# Overload for when acreate_container=True (returns Coroutine)
@overload
def create_container(
    name: str,
    expires_after: Optional[Dict[str, Any]] = None,
    file_ids: Optional[List[str]] = None,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    acreate_container: Literal[True],
    **kwargs,
) -> Coroutine[Any, Any, ContainerObject]:
    ...


@overload
def create_container(
    name: str,
    expires_after: Optional[Dict[str, Any]] = None,
    file_ids: Optional[List[str]] = None,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    acreate_container: Literal[False] = False,
    **kwargs,
) -> ContainerObject:
    ...

# fmt: on


@client
def create_container(
    name: str,
    expires_after: Optional[Dict[str, Any]] = None,
    file_ids: Optional[List[str]] = None,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Union[
    ContainerObject,
    Coroutine[Any, Any, ContainerObject],
]:
    """Create a container using the OpenAI Container API.

    Currently supports OpenAI

    Example:
    ```python
    import love_engine

    response = love_engine.create_container(
        name="My Container",
        custom_llm_provider="openai",
    )
    print(response)
    ```
    """
    local_vars = locals()
    try:
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.pop("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id")
        _is_async = kwargs.pop("async_call", False) is True

        # Check for mock response first
        mock_response = kwargs.get("mock_response")
        if mock_response is not None:
            if isinstance(mock_response, str):
                mock_response = json.loads(mock_response)

            response = ContainerObject(**mock_response)
            return response

        # get llm provider logic
        # Pass credential params explicitly since they're named args, not in kwargs
        love_engine_params = GenericLoveEngineParams(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            **kwargs,
        )
        # get provider config
        container_provider_config: Optional[BaseContainerConfig] = (
            ProviderConfigManager.get_provider_container_config(
                provider=love_engine.LlmProviders(custom_llm_provider),
            )
        )

        if container_provider_config is None:
            raise ValueError(
                f"container operations are not supported for {custom_llm_provider}"
            )

        local_vars.update(kwargs)
        # Get ContainerCreateOptionalRequestParams with only valid parameters
        container_create_optional_params: ContainerCreateOptionalRequestParams = (
            ContainerRequestUtils.get_requested_container_create_optional_param(
                local_vars
            )
        )

        # Get optional parameters for the container API
        container_create_request_params: Dict = (
            ContainerRequestUtils.get_optional_params_container_create(
                container_provider_config=container_provider_config,
                container_create_optional_params=container_create_optional_params,
            )
        )

        # Pre Call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model="",
            optional_params=dict(container_create_request_params),
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
                **container_create_request_params,
            },
            custom_llm_provider=custom_llm_provider,
        )

        # Set the correct call type for container creation
        love_engine_logging_obj.call_type = CallTypes.create_container.value

        container_obj = base_llm_http_handler.container_create_handler(
            name=name,
            container_create_request_params=container_create_request_params,
            container_provider_config=container_provider_config,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=extra_headers,
            timeout=timeout or DEFAULT_REQUEST_TIMEOUT,
            _is_async=_is_async,
        )

        # Encode container_id with provider/model metadata for routing
        if isinstance(container_obj, ContainerObject):
            container_obj = ContainerRequestUtils.encode_container_id_in_response(
                response_obj=container_obj,
                custom_llm_provider=custom_llm_provider,
                love_engine_metadata=kwargs.get("love_engine_metadata"),
                extra_body=extra_body,
            )

        return container_obj

    except Exception as e:
        raise love_engine.exception_type(
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


##### Container List #######################
@client
async def alist_containers(
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,  # default to 10 minutes
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> ContainerListResponse:
    """Asynchronously list containers.

    Parameters:
    - `after` (Optional[str]): A cursor for pagination
    - `limit` (Optional[int]): Number of items to return (1-100, default 20)
    - `order` (Optional[str]): Sort order ('asc' or 'desc', default 'desc')
    - `timeout` (int): Request timeout in seconds
    - `custom_llm_provider` (Literal["openai"]): The LLM provider to use
    - `extra_headers` (Optional[Dict[str, Any]]): Additional headers
    - `extra_query` (Optional[Dict[str, Any]]): Additional query parameters
    - `extra_body` (Optional[Dict[str, Any]]): Additional body parameters
    - `kwargs` (dict): Additional keyword arguments

    Returns:
    - `response` (ContainerListResponse): The list of containers
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["async_call"] = True

        func = partial(
            list_containers,
            after=after,
            limit=limit,
            order=order,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
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
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


# fmt: off

@overload
def list_containers(
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    alist_containers: Literal[True],
    **kwargs,
) -> Coroutine[Any, Any, ContainerListResponse]:
    ...


@overload
def list_containers(
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    alist_containers: Literal[False] = False,
    **kwargs,
) -> ContainerListResponse:
    ...

# fmt: on


@client
def list_containers(
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Union[
    ContainerListResponse,
    Coroutine[Any, Any, ContainerListResponse],
]:
    """List containers using the OpenAI Container API.

    Currently supports OpenAI
    """
    local_vars = locals()
    try:
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.pop("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id")
        _is_async = kwargs.pop("async_call", False) is True

        # Check for mock response first
        mock_response = kwargs.get("mock_response")
        if mock_response is not None:
            if isinstance(mock_response, str):
                mock_response = json.loads(mock_response)

            response = ContainerListResponse(**mock_response)
            return response

        # get llm provider logic
        # Pass credential params explicitly since they're named args, not in kwargs
        love_engine_params = GenericLoveEngineParams(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            **kwargs,
        )
        # get provider config
        container_provider_config: Optional[BaseContainerConfig] = (
            ProviderConfigManager.get_provider_container_config(
                provider=love_engine.LlmProviders(custom_llm_provider),
            )
        )

        if container_provider_config is None:
            raise ValueError(
                f"Container provider config not found for provider: {custom_llm_provider}"
            )

        # Get container list request parameters
        container_list_optional_params: ContainerListOptionalRequestParams = (
            ContainerRequestUtils.get_requested_container_list_optional_param(
                local_vars
            )
        )

        # Pre Call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model="",
            optional_params=dict(container_list_optional_params),
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
                **container_list_optional_params,
            },
            custom_llm_provider=custom_llm_provider,
        )

        # Set the correct call type
        love_engine_logging_obj.call_type = CallTypes.list_containers.value

        return base_llm_http_handler.container_list_handler(
            container_provider_config=container_provider_config,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            after=after,
            limit=limit,
            order=order,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout or DEFAULT_REQUEST_TIMEOUT,
            _is_async=_is_async,
        )

    except Exception as e:
        raise love_engine.exception_type(
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


##### Container Retrieve #######################
@client
async def aretrieve_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> ContainerObject:
    """Asynchronously retrieve a container.

    Parameters:
    - `container_id` (str): The ID of the container to retrieve
    - `timeout` (int): Request timeout in seconds
    - `custom_llm_provider` (Literal["openai"]): The LLM provider to use
    - `extra_headers` (Optional[Dict[str, Any]]): Additional headers
    - `extra_query` (Optional[Dict[str, Any]]): Additional query parameters
    - `extra_body` (Optional[Dict[str, Any]]): Additional body parameters
    - `kwargs` (dict): Additional keyword arguments

    Returns:
    - `response` (ContainerObject): The container object
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["async_call"] = True

        func = partial(
            retrieve_container,
            container_id=container_id,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
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
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


# fmt: off

@overload
def retrieve_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    aretrieve_container: Literal[True],
    **kwargs,
) -> Coroutine[Any, Any, ContainerObject]:
    ...


@overload
def retrieve_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    aretrieve_container: Literal[False] = False,
    **kwargs,
) -> ContainerObject:
    ...

# fmt: on


@client
def retrieve_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Union[
    ContainerObject,
    Coroutine[Any, Any, ContainerObject],
]:
    """Retrieve a container using the OpenAI Container API.

    Currently supports OpenAI
    """
    local_vars = locals()
    try:
        resolved_custom_llm_provider: str = custom_llm_provider
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.pop("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id")
        _is_async = kwargs.pop("async_call", False) is True

        # Check for mock response first
        mock_response = kwargs.get("mock_response")
        if mock_response is not None:
            if isinstance(mock_response, str):
                mock_response = json.loads(mock_response)

            response = ContainerObject(**mock_response)
            return response

        # get llm provider logic
        # Pass credential params explicitly since they're named args, not in kwargs
        love_engine_params = GenericLoveEngineParams(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            **kwargs,
        )

        # Decode container ID and extract provider info
        original_container_id, resolved_custom_llm_provider, love_engine_params = (
            decode_managed_container_id_for_request(
                container_id=container_id,
                custom_llm_provider=custom_llm_provider,
                love_engine_params=love_engine_params,
            )
        )
        # True when input was a love_engine-managed ID (any length); needed to re-encode output for routing affinity
        was_encoded = original_container_id != container_id

        # get provider config
        container_provider_config: Optional[BaseContainerConfig] = (
            ProviderConfigManager.get_provider_container_config(
                provider=love_engine.LlmProviders(resolved_custom_llm_provider),
            )
        )

        if container_provider_config is None:
            raise ValueError(
                f"Container provider config not found for provider: {resolved_custom_llm_provider}"
            )

        # Pre Call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model="",
            optional_params={},
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=resolved_custom_llm_provider,
        )

        # Set the correct call type
        love_engine_logging_obj.call_type = CallTypes.retrieve_container.value

        container_obj = base_llm_http_handler.container_retrieve_handler(
            container_id=original_container_id,  # Use decoded original ID
            container_provider_config=container_provider_config,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout or DEFAULT_REQUEST_TIMEOUT,
            _is_async=_is_async,
        )

        # Encode container_id with provider/model metadata for routing
        # If input was encoded, preserve encoding in output using the decoded model_id
        if isinstance(container_obj, ContainerObject):
            # If input was encoded, use model_id from decoded params
            love_engine_metadata = kwargs.get("love_engine_metadata", {})
            if was_encoded and love_engine_params.get("model_id"):
                # Inject model_id from decoded container_id into love_engine_metadata
                if not love_engine_metadata:
                    love_engine_metadata = {}
                if "model_info" not in love_engine_metadata:
                    love_engine_metadata["model_info"] = {}
                love_engine_metadata["model_info"]["id"] = love_engine_params["model_id"]

            container_obj = ContainerRequestUtils.encode_container_id_in_response(
                response_obj=container_obj,
                custom_llm_provider=resolved_custom_llm_provider,
                love_engine_metadata=love_engine_metadata,
                extra_body=None,
            )

        return container_obj

    except Exception as e:
        raise love_engine.exception_type(
            model="",
            custom_llm_provider=resolved_custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


##### Container Delete #######################
@client
async def adelete_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> DeleteContainerResult:
    """Asynchronously delete a container.

    Parameters:
    - `container_id` (str): The ID of the container to delete
    - `timeout` (int): Request timeout in seconds
    - `custom_llm_provider` (Literal["openai"]): The LLM provider to use
    - `extra_headers` (Optional[Dict[str, Any]]): Additional headers
    - `extra_query` (Optional[Dict[str, Any]]): Additional query parameters
    - `extra_body` (Optional[Dict[str, Any]]): Additional body parameters
    - `kwargs` (dict): Additional keyword arguments

    Returns:
    - `response` (DeleteContainerResult): The deletion result
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["async_call"] = True

        func = partial(
            delete_container,
            container_id=container_id,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
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
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


# fmt: off

@overload
def delete_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    adelete_container: Literal[True],
    **kwargs,
) -> Coroutine[Any, Any, DeleteContainerResult]:
    ...


@overload
def delete_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    adelete_container: Literal[False] = False,
    **kwargs,
) -> DeleteContainerResult:
    ...

# fmt: on


@client
def delete_container(
    container_id: str,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Union[
    DeleteContainerResult,
    Coroutine[Any, Any, DeleteContainerResult],
]:
    """Delete a container using the OpenAI Container API.

    Currently supports OpenAI
    """
    local_vars = locals()
    try:
        resolved_custom_llm_provider: str = custom_llm_provider
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.pop("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id")
        _is_async = kwargs.pop("async_call", False) is True

        # Check for mock response first
        mock_response = kwargs.get("mock_response")
        if mock_response is not None:
            if isinstance(mock_response, str):
                mock_response = json.loads(mock_response)

            response = DeleteContainerResult(**mock_response)
            return response

        # get llm provider logic
        # Pass credential params explicitly since they're named args, not in kwargs
        love_engine_params = GenericLoveEngineParams(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            **kwargs,
        )

        # Decode container ID and extract provider info
        original_container_id, resolved_custom_llm_provider, love_engine_params = (
            decode_managed_container_id_for_request(
                container_id=container_id,
                custom_llm_provider=custom_llm_provider,
                love_engine_params=love_engine_params,
            )
        )
        # True when input was a love_engine-managed ID (any length); needed to re-encode output for routing affinity
        was_encoded = original_container_id != container_id

        # get provider config
        container_provider_config: Optional[BaseContainerConfig] = (
            ProviderConfigManager.get_provider_container_config(
                provider=love_engine.LlmProviders(resolved_custom_llm_provider),
            )
        )

        if container_provider_config is None:
            raise ValueError(
                f"Container provider config not found for provider: {resolved_custom_llm_provider}"
            )

        # Pre Call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model="",
            optional_params={},
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=resolved_custom_llm_provider,
        )

        # Set the correct call type
        love_engine_logging_obj.call_type = CallTypes.delete_container.value

        delete_result = base_llm_http_handler.container_delete_handler(
            container_id=original_container_id,  # Use decoded original ID
            container_provider_config=container_provider_config,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout or DEFAULT_REQUEST_TIMEOUT,
            _is_async=_is_async,
        )

        # Encode container_id in response with provider/model metadata for routing
        # If input was encoded, preserve encoding in output using the decoded model_id
        if isinstance(delete_result, DeleteContainerResult):
            # If input was encoded, use model_id from decoded params
            love_engine_metadata = kwargs.get("love_engine_metadata", {})
            if was_encoded and love_engine_params.get("model_id"):
                # Inject model_id from decoded container_id into love_engine_metadata
                if not love_engine_metadata:
                    love_engine_metadata = {}
                if "model_info" not in love_engine_metadata:
                    love_engine_metadata["model_info"] = {}
                love_engine_metadata["model_info"]["id"] = love_engine_params["model_id"]

            delete_result = ContainerRequestUtils.encode_container_id_in_response(
                response_obj=delete_result,
                custom_llm_provider=resolved_custom_llm_provider,
                love_engine_metadata=love_engine_metadata,
                extra_body=None,
            )

        return delete_result

    except Exception as e:
        raise love_engine.exception_type(
            model="",
            custom_llm_provider=resolved_custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


##### Container Files List #######################
@client
async def alist_container_files(
    container_id: str,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,  # default to 10 minutes
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> ContainerFileListResponse:
    """Asynchronously list files in a container.

    Parameters:
    - `container_id` (str): The ID of the container
    - `after` (Optional[str]): A cursor for pagination
    - `limit` (Optional[int]): Number of items to return (1-100, default 20)
    - `order` (Optional[str]): Sort order ('asc' or 'desc', default 'desc')
    - `timeout` (int): Request timeout in seconds
    - `custom_llm_provider` (Literal["openai"]): The LLM provider to use
    - `extra_headers` (Optional[Dict[str, Any]]): Additional headers
    - `extra_query` (Optional[Dict[str, Any]]): Additional query parameters
    - `extra_body` (Optional[Dict[str, Any]]): Additional body parameters
    - `kwargs` (dict): Additional keyword arguments

    Returns:
    - `response` (ContainerFileListResponse): The list of container files
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["async_call"] = True

        func = partial(
            list_container_files,
            container_id=container_id,
            after=after,
            limit=limit,
            order=order,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
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
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


# fmt: off

@overload
def list_container_files(
    container_id: str,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    alist_container_files: Literal[True],
    **kwargs,
) -> Coroutine[Any, Any, ContainerFileListResponse]:
    ...


@overload
def list_container_files(
    container_id: str,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    alist_container_files: Literal[False] = False,
    **kwargs,
) -> ContainerFileListResponse:
    ...

# fmt: on


@client
def list_container_files(
    container_id: str,
    after: Optional[str] = None,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Union[
    ContainerFileListResponse,
    Coroutine[Any, Any, ContainerFileListResponse],
]:
    """List files in a container using the OpenAI Container API.

    Currently supports OpenAI
    """
    local_vars = locals()
    try:
        resolved_custom_llm_provider: str = custom_llm_provider
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.pop("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id")
        _is_async = kwargs.pop("async_call", False) is True

        # Check for mock response first
        mock_response = kwargs.get("mock_response")
        if mock_response is not None:
            if isinstance(mock_response, str):
                mock_response = json.loads(mock_response)

            response = ContainerFileListResponse(**mock_response)
            return response

        # get llm provider logic
        # Pass credential params explicitly since they're named args, not in kwargs
        love_engine_params = GenericLoveEngineParams(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            **kwargs,
        )

        # Decode container ID and extract provider info
        original_container_id, resolved_custom_llm_provider, love_engine_params = (
            decode_managed_container_id_for_request(
                container_id=container_id,
                custom_llm_provider=custom_llm_provider,
                love_engine_params=love_engine_params,
            )
        )

        # get provider config
        container_provider_config: Optional[BaseContainerConfig] = (
            ProviderConfigManager.get_provider_container_config(
                provider=love_engine.LlmProviders(resolved_custom_llm_provider),
            )
        )

        if container_provider_config is None:
            raise ValueError(
                f"Container provider config not found for provider: {resolved_custom_llm_provider}"
            )

        # Pre Call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model="",
            optional_params={
                "container_id": container_id,
                "after": after,
                "limit": limit,
                "order": order,
            },
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=resolved_custom_llm_provider,
        )

        # Set the correct call type
        love_engine_logging_obj.call_type = CallTypes.list_container_files.value

        return base_llm_http_handler.container_file_list_handler(
            container_id=original_container_id,  # Use decoded original ID
            container_provider_config=container_provider_config,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            after=after,
            limit=limit,
            order=order,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout or DEFAULT_REQUEST_TIMEOUT,
            _is_async=_is_async,
        )

    except Exception as e:
        raise love_engine.exception_type(
            model="",
            custom_llm_provider=resolved_custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


##### Container File Upload #######################
@client
async def aupload_container_file(
    container_id: str,
    file: FileTypes,
    timeout=600,  # default to 10 minutes
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> ContainerFileObject:
    """Asynchronously upload a file to a container.

    This endpoint allows uploading files directly to a container session,
    supporting various file types like CSV, Excel, Python scripts, etc.

    Parameters:
    - `container_id` (str): The ID of the container to upload the file to
    - `file` (FileTypes): The file to upload. Can be:
        - A tuple of (filename, content, content_type)
        - A tuple of (filename, content)
        - A file-like object with read() method
        - Bytes
        - A string path to a file
    - `timeout` (int): Request timeout in seconds
    - `custom_llm_provider` (Literal["openai"]): The LLM provider to use
    - `extra_headers` (Optional[Dict[str, Any]]): Additional headers
    - `extra_query` (Optional[Dict[str, Any]]): Additional query parameters
    - `extra_body` (Optional[Dict[str, Any]]): Additional body parameters
    - `kwargs` (dict): Additional keyword arguments

    Returns:
    - `response` (ContainerFileObject): The uploaded file object

    Example:
    ```python
    import love_engine

    # Upload a CSV file
    response = await love_engine.aupload_container_file(
        container_id="container_abc123",
        file=("data.csv", open("data.csv", "rb").read(), "text/csv"),
        custom_llm_provider="openai",
    )
    print(response)
    ```
    """
    local_vars = locals()
    try:
        loop = asyncio.get_event_loop()
        kwargs["async_call"] = True

        func = partial(
            upload_container_file,
            container_id=container_id,
            file=file,
            timeout=timeout,
            custom_llm_provider=custom_llm_provider,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
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
            model="",
            custom_llm_provider=custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )


# fmt: off

@overload
def upload_container_file(
    container_id: str,
    file: FileTypes,
    timeout=600,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    aupload_container_file: Literal[True],
    **kwargs,
) -> Coroutine[Any, Any, ContainerFileObject]:
    ...


@overload
def upload_container_file(
    container_id: str,
    file: FileTypes,
    timeout=600,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    *,
    aupload_container_file: Literal[False] = False,
    **kwargs,
) -> ContainerFileObject:
    ...

# fmt: on


@client
def upload_container_file(
    container_id: str,
    file: FileTypes,
    timeout=600,  # default to 10 minutes
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    api_version: Optional[str] = None,
    custom_llm_provider: Literal["openai", "azure", "azure_text"] = "openai",
    extra_headers: Optional[Dict[str, Any]] = None,
    extra_query: Optional[Dict[str, Any]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Union[
    ContainerFileObject,
    Coroutine[Any, Any, ContainerFileObject],
]:
    """Upload a file to a container using the OpenAI Container API.

    This endpoint allows uploading files directly to a container session,
    supporting various file types like CSV, Excel, Python scripts, JSON, etc.
    This is useful when /chat/completions or /responses sends files to the
    container but the input file type is limited to PDF. This endpoint lets
    you work with other file types.

    Currently supports OpenAI

    Example:
    ```python
    import love_engine

    # Upload a CSV file
    response = love_engine.upload_container_file(
        container_id="container_abc123",
        file=("data.csv", open("data.csv", "rb").read(), "text/csv"),
        custom_llm_provider="openai",
    )
    print(response)

    # Upload a Python script
    response = love_engine.upload_container_file(
        container_id="container_abc123",
        file=("script.py", b"print('hello world')", "text/x-python"),
        custom_llm_provider="openai",
    )
    print(response)
    ```
    """
    from love_engine.llms.custom_httpx.container_handler import generic_container_handler

    local_vars = locals()
    try:
        resolved_custom_llm_provider: str = custom_llm_provider
        love_engine_logging_obj: LoveEngineLoggingObj = kwargs.pop("love_engine_logging_obj")  # type: ignore
        love_engine_call_id: Optional[str] = kwargs.get("love_engine_call_id")
        _is_async = kwargs.pop("async_call", False) is True

        # Check for mock response first
        mock_response = kwargs.get("mock_response")
        if mock_response is not None:
            if isinstance(mock_response, str):
                mock_response = json.loads(mock_response)

            response = ContainerFileObject(**mock_response)
            return response

        # get llm provider logic
        # Pass credential params explicitly since they're named args, not in kwargs
        love_engine_params = GenericLoveEngineParams(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            **kwargs,
        )

        # Decode container ID and extract provider info
        original_container_id, resolved_custom_llm_provider, love_engine_params = (
            decode_managed_container_id_for_request(
                container_id=container_id,
                custom_llm_provider=custom_llm_provider,
                love_engine_params=love_engine_params,
            )
        )

        # get provider config
        container_provider_config: Optional[BaseContainerConfig] = (
            ProviderConfigManager.get_provider_container_config(
                provider=love_engine.LlmProviders(resolved_custom_llm_provider),
            )
        )

        if container_provider_config is None:
            raise ValueError(
                f"Container provider config not found for provider: {resolved_custom_llm_provider}"
            )

        # Pre Call logging
        love_engine_logging_obj.update_from_kwargs(
            kwargs=kwargs,
            model="",
            optional_params={"container_id": container_id},
            love_engine_params={
                "love_engine_call_id": love_engine_call_id,
            },
            custom_llm_provider=resolved_custom_llm_provider,
        )

        # Set the correct call type
        love_engine_logging_obj.call_type = CallTypes.upload_container_file.value

        return generic_container_handler.handle(
            endpoint_name="upload_container_file",
            container_provider_config=container_provider_config,
            love_engine_params=love_engine_params,
            logging_obj=love_engine_logging_obj,
            extra_headers=extra_headers,
            extra_query=extra_query,
            timeout=timeout or DEFAULT_REQUEST_TIMEOUT,
            _is_async=_is_async,
            container_id=original_container_id,  # Use decoded original ID
            file=file,
        )

    except Exception as e:
        raise love_engine.exception_type(
            model="",
            custom_llm_provider=resolved_custom_llm_provider,
            original_exception=e,
            completion_kwargs=local_vars,
            extra_kwargs=kwargs,
        )
