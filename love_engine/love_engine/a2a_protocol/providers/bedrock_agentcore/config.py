"""
Bedrock AgentCore A2A provider configuration.
"""

from typing import Any, AsyncIterator, Dict, Optional

from love_engine.a2a_protocol.providers.base import BaseA2AProviderConfig
from love_engine.a2a_protocol.providers.bedrock_agentcore.handler import (
    BedrockAgentCoreA2AHandler,
)


class BedrockAgentCoreA2AConfig(BaseA2AProviderConfig):
    """
    Provider configuration for Bedrock AgentCore A2A-native agents.

    AgentCore agents that speak A2A natively expect the full JSON-RPC envelope.
    This config bypasses the completion bridge and forwards requests directly,
    deriving the endpoint URL from the model ARN and signing with SigV4/JWT.
    """

    async def handle_non_streaming(
        self,
        request_id: str,
        params: Dict[str, Any],
        api_base: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Handle non-streaming request to AgentCore A2A agent."""
        love_engine_params = kwargs.get("love_engine_params")
        if not love_engine_params:
            raise ValueError(
                "love_engine_params is required for BedrockAgentCoreA2AConfig "
                "(must contain model with AgentCore ARN)"
            )
        return await BedrockAgentCoreA2AHandler.handle_non_streaming(
            request_id=request_id,
            params=params,
            love_engine_params=love_engine_params,
            agent_extra_headers=kwargs.get("agent_extra_headers"),
        )

    async def handle_streaming(
        self,
        request_id: str,
        params: Dict[str, Any],
        api_base: Optional[str] = None,
        **kwargs,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Handle streaming request to AgentCore A2A agent."""
        love_engine_params = kwargs.get("love_engine_params")
        if not love_engine_params:
            raise ValueError(
                "love_engine_params is required for BedrockAgentCoreA2AConfig "
                "(must contain model with AgentCore ARN)"
            )
        async for chunk in BedrockAgentCoreA2AHandler.handle_streaming(
            request_id=request_id,
            params=params,
            love_engine_params=love_engine_params,
            agent_extra_headers=kwargs.get("agent_extra_headers"),
        ):
            yield chunk
