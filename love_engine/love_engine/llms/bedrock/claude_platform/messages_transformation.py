from typing import Any, Dict, List, Optional, Tuple

import love_engine
from love_engine.llms.anthropic.experimental_pass_through.messages.transformation import (
    DEFAULT_ANTHROPIC_API_VERSION,
    AnthropicMessagesConfig,
)
from love_engine.secret_managers.main import get_secret_str
from love_engine.types.router import GenericLoveEngineParams

from .common_utils import BedrockClaudePlatformMixin, strip_claude_platform_route


class BedrockClaudePlatformMessagesConfig(
    BedrockClaudePlatformMixin, AnthropicMessagesConfig
):
    def validate_anthropic_messages_environment(
        self,
        headers: dict,
        model: str,
        messages: List[Any],
        optional_params: dict,
        love_engine_params: dict,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> Tuple[dict, Optional[str]]:
        workspace_id = self._get_workspace_id(optional_params, love_engine_params)
        if workspace_id is None:
            raise love_engine.AuthenticationError(
                message=(
                    "Missing workspace ID for Claude Platform on AWS. Pass "
                    "`workspace_id` or configure the provider workspace setting."
                ),
                llm_provider="bedrock",
                model=model,
            )

        resolved_api_key = api_key or get_secret_str("ANTHROPIC_AWS_API_KEY")
        headers = {
            **headers,
            "anthropic-version": headers.get(
                "anthropic-version", DEFAULT_ANTHROPIC_API_VERSION
            ),
            "content-type": headers.get("content-type", "application/json"),
            "anthropic-workspace-id": workspace_id,
        }
        if resolved_api_key and "x-api-key" not in headers:
            headers["x-api-key"] = resolved_api_key

        headers = self._update_headers_with_anthropic_beta(
            headers=headers,
            optional_params=optional_params,
        )

        return headers, api_base

    def transform_anthropic_messages_request(
        self,
        model: str,
        messages: List[Dict],
        anthropic_messages_optional_request_params: Dict,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Dict:
        return super().transform_anthropic_messages_request(
            model=strip_claude_platform_route(model),
            messages=messages,
            anthropic_messages_optional_request_params=anthropic_messages_optional_request_params,
            love_engine_params=love_engine_params,
            headers=headers,
        )
