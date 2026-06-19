from typing import Any, AsyncIterator, Dict, Optional

from love_engine.a2a_protocol.love_engine_completion_bridge.handler import (
    A2A_USER_API_KEY_HASH_PARAM,
    A2ACompletionBridgeHandler,
)
from love_engine.a2a_protocol.providers.base import BaseA2AProviderConfig
from love_engine.llms.langflow.a2a import merge_a2a_session_into_love_engine_params


class LangFlowA2AConfig(BaseA2AProviderConfig):
    """A2A bridge for LangFlow: scopes contextId to the authenticated key as the
    LangFlow session_id, then uses completion."""

    async def handle_non_streaming(
        self,
        request_id: str,
        params: Dict[str, Any],
        api_base: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        love_engine_params = kwargs.get("love_engine_params")
        if not love_engine_params:
            raise ValueError(
                "love_engine_params is required for LangFlowA2AConfig "
                "(must contain custom_llm_provider and model)"
            )
        love_engine_params = merge_a2a_session_into_love_engine_params(
            love_engine_params, params, love_engine_params.get(A2A_USER_API_KEY_HASH_PARAM)
        )
        return await A2ACompletionBridgeHandler.handle_non_streaming(
            request_id=request_id,
            params=params,
            love_engine_params=love_engine_params,
            api_base=api_base,
            _skip_a2a_provider_routing=True,
        )

    async def handle_streaming(
        self,
        request_id: str,
        params: Dict[str, Any],
        api_base: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        love_engine_params = kwargs.get("love_engine_params")
        if not love_engine_params:
            raise ValueError(
                "love_engine_params is required for LangFlowA2AConfig "
                "(must contain custom_llm_provider and model)"
            )
        love_engine_params = merge_a2a_session_into_love_engine_params(
            love_engine_params, params, love_engine_params.get(A2A_USER_API_KEY_HASH_PARAM)
        )
        async for chunk in A2ACompletionBridgeHandler.handle_streaming(
            request_id=request_id,
            params=params,
            love_engine_params=love_engine_params,
            api_base=api_base,
            _skip_a2a_provider_routing=True,
        ):
            yield chunk
