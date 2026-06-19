"""
Transformation for Bedrock Mantle (Claude Mythos Preview)

https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-mythos-preview.html

The bedrock-mantle endpoint uses the Anthropic Messages API format but is served
at a different endpoint (bedrock-mantle.{region}.api.aws) with AWS SigV4 auth.
"""

from typing import TYPE_CHECKING, Any, List, Optional

from love_engine.llms.bedrock.chat.invoke_transformations.anthropic_claude3_transformation import (
    AmazonAnthropicClaudeConfig,
)
from love_engine.types.llms.openai import AllMessageValues

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as _LoveEngineLoggingObj

    LoveEngineLoggingObj = _LoveEngineLoggingObj
else:
    LoveEngineLoggingObj = Any

MANTLE_ENDPOINT_TEMPLATE = (
    "https://bedrock-mantle.{region}.api.aws/anthropic/v1/messages"
)


class AmazonMantleConfig(AmazonAnthropicClaudeConfig):
    """
    Config for the bedrock-mantle endpoint (Claude Mythos Preview).

    Uses the Anthropic Messages API format with AWS SigV4 auth, but at a
    different endpoint from bedrock-runtime. Model ID goes in the request body.

    Usage: model="bedrock/mantle/anthropic.claude-mythos-preview"
    """

    def get_complete_url(
        self,
        api_base: Optional[str],
        api_key: Optional[str],
        model: str,
        optional_params: dict,
        love_engine_params: dict,
        stream: Optional[bool] = None,
    ) -> str:
        region = self._get_aws_region_name(optional_params=optional_params, model=model)
        return MANTLE_ENDPOINT_TEMPLATE.format(region=region)

    def validate_environment(
        self,
        headers: dict,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> dict:
        headers = super().validate_environment(
            headers=headers,
            model=model,
            messages=messages,
            optional_params=optional_params,
            love_engine_params=love_engine_params,
            api_key=api_key,
            api_base=api_base,
        )
        project_id = love_engine_params.get("aws_bedrock_project_id")
        if project_id:
            headers["anthropic-workspace"] = project_id
        return headers

    def transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        headers: dict,
    ) -> dict:
        # Strip the "mantle/" routing prefix to get the real model ID
        model_id = model.replace("mantle/", "", 1)

        request = self._build_bedrock_anthropic_request_base(
            model=model_id,
            messages=messages,
            optional_params=optional_params,
            love_engine_params=love_engine_params,
            headers=headers,
        )
        # The parent strips "model" from the body (Invoke API puts it in URL).
        # The mantle endpoint (Messages API) requires "model" in the body.
        request["model"] = model_id
        return request

    async def async_transform_request(
        self,
        model: str,
        messages: List[AllMessageValues],
        optional_params: dict,
        love_engine_params: dict,
        headers: dict,
    ) -> dict:
        model_id = model.replace("mantle/", "", 1)

        request = self._build_bedrock_anthropic_request_base(
            model=model_id,
            messages=messages,
            optional_params=optional_params,
            love_engine_params=love_engine_params,
            headers=headers,
        )
        await self._async_convert_document_url_sources_to_base64(request)
        request["model"] = model_id
        return request
