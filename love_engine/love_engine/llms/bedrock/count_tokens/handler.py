"""
AWS Bedrock CountTokens API handler.

Simplified handler leveraging existing love_engine Bedrock infrastructure.
"""

from typing import Any, Dict

import httpx

import love_engine
from love_engine._logging import verbose_logger
from love_engine.llms.bedrock.common_utils import BedrockError
from love_engine.llms.bedrock.count_tokens.transformation import BedrockCountTokensConfig
from love_engine.llms.custom_httpx.http_handler import get_async_httpx_client


class BedrockCountTokensHandler(BedrockCountTokensConfig):
    """
    Simplified handler for AWS Bedrock CountTokens API requests.

    Uses existing love_engine infrastructure for authentication and request handling.
    """

    async def handle_count_tokens_request(
        self,
        request_data: Dict[str, Any],
        love_engine_params: Dict[str, Any],
        resolved_model: str,
    ) -> Dict[str, Any]:
        """
        Handle a CountTokens request using existing love_engine patterns.

        Args:
            request_data: The incoming request payload
            love_engine_params: love_engine configuration parameters
            resolved_model: The actual model ID resolved from router

        Returns:
            Dictionary containing token count response
        """
        try:
            # Validate the request
            self.validate_count_tokens_request(request_data)

            verbose_logger.debug(
                f"Processing CountTokens request for resolved model: {resolved_model}"
            )

            # Get AWS region using existing love_engine function
            aws_region_name = self._get_aws_region_name(
                optional_params=love_engine_params,
                model=resolved_model,
                model_id=None,
            )

            verbose_logger.debug(f"Retrieved AWS region: {aws_region_name}")

            # Transform request to Bedrock format (supports both Converse and InvokeModel)
            bedrock_request = self.transform_anthropic_to_bedrock_count_tokens(
                request_data=request_data
            )

            verbose_logger.debug(f"Transformed request: {bedrock_request}")

            # Get endpoint URL using simplified function
            api_base = love_engine_params.get("api_base", None)
            aws_bedrock_runtime_endpoint = love_engine_params.get(
                "aws_bedrock_runtime_endpoint", None
            )
            endpoint_url = self.get_bedrock_count_tokens_endpoint(
                model=resolved_model,
                aws_region_name=aws_region_name,
                api_base=api_base,
                aws_bedrock_runtime_endpoint=aws_bedrock_runtime_endpoint,
            )

            verbose_logger.debug(f"Making request to: {endpoint_url}")

            # Use existing _sign_request method from BaseAWSLLM
            # Extract api_key for bearer token auth if provided
            api_key = love_engine_params.get("api_key", None)
            headers = {"Content-Type": "application/json"}
            signed_headers, signed_body = self._sign_request(
                service_name="bedrock",
                headers=headers,
                optional_params=love_engine_params,
                request_data=bedrock_request,
                api_base=endpoint_url,
                model=resolved_model,
                api_key=api_key,
            )

            async_client = get_async_httpx_client(
                llm_provider=love_engine.LlmProviders.BEDROCK
            )

            response = await async_client.post(
                endpoint_url,
                headers=signed_headers,
                data=signed_body,
                timeout=30.0,
            )

            verbose_logger.debug(f"Response status: {response.status_code}")

            if response.status_code != 200:
                error_text = response.text
                verbose_logger.error(f"AWS Bedrock error: {error_text}")
                raise BedrockError(
                    status_code=response.status_code,
                    message=error_text,
                )

            bedrock_response = response.json()

            verbose_logger.debug(f"Bedrock response: {bedrock_response}")

            # Transform response back to expected format
            final_response = self.transform_bedrock_response_to_anthropic(
                bedrock_response
            )

            verbose_logger.debug(f"Final response: {final_response}")

            return final_response

        except BedrockError:
            # Re-raise Bedrock exceptions as-is
            raise
        except httpx.HTTPStatusError as e:
            # HTTP errors - preserve the actual status code
            verbose_logger.error(f"HTTP error in CountTokens handler: {str(e)}")
            raise BedrockError(
                status_code=e.response.status_code,
                message=e.response.text,
            )
        except Exception as e:
            verbose_logger.error(f"Error in CountTokens handler: {str(e)}")
            raise BedrockError(
                status_code=500,
                message=f"CountTokens processing error: {str(e)}",
            )
