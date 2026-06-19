"""
Google AI Studio Interactions API configuration.

Per OpenAPI spec (https://ai.google.dev/static/api/interactions.openapi.json):
- Create: POST https://generativelanguage.googleapis.com/{api_version}/interactions
- Get: GET https://generativelanguage.googleapis.com/{api_version}/interactions/{interaction_id}
- Delete: DELETE https://generativelanguage.googleapis.com/{api_version}/interactions/{interaction_id}

Schema versioning:
- Default (Api-Revision: 2026-05-20): new `steps` schema.
- Legacy (Api-Revision: 2026-05-07): old `outputs` schema, controlled via
  love_engine.use_legacy_interactions_schema = True. Remove flag after June 8, 2026.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import httpx

import love_engine

from love_engine._logging import verbose_logger
from love_engine.love_engine_core_utils.core_helpers import process_response_headers
from love_engine.love_engine_core_utils.url_utils import encode_url_path_segment
from love_engine.llms.base_llm.interactions.transformation import BaseInteractionsAPIConfig
from love_engine.llms.gemini.common_utils import GeminiError, GeminiModelInfo
from love_engine.types.interactions import (
    CancelInteractionResult,
    DeleteInteractionResult,
    InteractionInput,
    InteractionsAPIOptionalRequestParams,
    InteractionsAPIResponse,
    InteractionsAPIStreamingResponse,
)
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import LlmProviders

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as _LoveEngineLoggingObj

    LoveEngineLoggingObj = _LoveEngineLoggingObj
else:
    LoveEngineLoggingObj = Any


class GoogleAIStudioInteractionsConfig(BaseInteractionsAPIConfig):
    """
    Configuration for Google AI Studio Interactions API.

    Minimal config - we follow the OpenAPI spec directly with no transformation.
    """

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.GEMINI

    @property
    def api_version(self) -> str:
        return "v1beta"

    def get_supported_params(self, model: str) -> List[str]:
        """Per OpenAPI spec CreateModelInteractionParams."""
        return [
            "model",
            "agent",
            "input",
            "tools",
            "system_instruction",
            "generation_config",
            "stream",
            "store",
            "background",
            "environment",
            "response_modalities",
            "response_format",
            "response_mime_type",
            "previous_interaction_id",
        ]

    def validate_environment(
        self,
        headers: dict,
        model: str,
        love_engine_params: Optional[GenericLoveEngineParams],
    ) -> dict:
        """Google AI Studio uses x-goog-api-key header for authentication."""
        headers = headers or {}
        headers["Content-Type"] = "application/json"
        if love_engine_params:
            api_key = GeminiModelInfo.get_api_key(love_engine_params.get("api_key"))
            if api_key:
                headers["x-goog-api-key"] = api_key

        # Inject the Api-Revision header to select the response schema.
        # Default to the new `steps` schema unless the operator has opted out.
        # Remove this conditional after June 8, 2026 and always use 2026-05-20.
        if love_engine.use_legacy_interactions_schema:
            headers["Api-Revision"] = "2026-05-07"
        else:
            headers["Api-Revision"] = "2026-05-20"

        return headers

    def get_complete_url(
        self,
        api_base: Optional[str],
        model: Optional[str],
        agent: Optional[str] = None,
        love_engine_params: Optional[dict] = None,
        stream: Optional[bool] = None,
    ) -> str:
        """POST /{api_version}/interactions"""
        love_engine_params = love_engine_params or {}
        api_base = GeminiModelInfo.get_api_base(api_base)
        api_key = GeminiModelInfo.get_api_key(love_engine_params.get("api_key"))

        if not api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable."
            )

        if stream:
            return f"{api_base}/{self.api_version}/interactions?alt=sse"

        return f"{api_base}/{self.api_version}/interactions"

    def transform_request(
        self,
        model: Optional[str],
        agent: Optional[str],
        input: Optional[InteractionInput],
        optional_params: InteractionsAPIOptionalRequestParams,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Dict:
        """
        Build request body per OpenAPI spec.

        When on the new schema (use_legacy_interactions_schema=False, the default):
        - ``response_mime_type`` is folded into ``response_format`` and stripped from
          the body (the field was removed in Api-Revision 2026-05-20).
        - ``generation_config.image_config`` is moved to a ``response_format`` entry
          with ``"type": "image"`` (also removed from generation_config in 2026-05-20).

        When on the legacy schema (use_legacy_interactions_schema=True):
        - All fields are forwarded as-is.
        """
        use_legacy: bool = love_engine.use_legacy_interactions_schema

        request_body: Dict[str, Any] = {}

        # Model or Agent (one required)
        if model:
            request_body["model"] = GeminiModelInfo.get_base_model(model) or model
        elif agent:
            request_body["agent"] = agent
        else:
            raise ValueError("Either 'model' or 'agent' must be provided")

        # Input
        if input is not None:
            request_body["input"] = input

        # Pass through optional params — legacy schema keeps all fields as-is.
        optional_keys = [
            "tools",
            "system_instruction",
            "stream",
            "store",
            "background",
            "environment",
            "response_modalities",
            "previous_interaction_id",
        ]
        for key in optional_keys:
            if optional_params.get(key) is not None:
                request_body[key] = optional_params[key]

        if use_legacy:
            # Legacy schema: forward response_mime_type and response_format as-is.
            for key in ("response_format", "response_mime_type", "generation_config"):
                if optional_params.get(key) is not None:
                    request_body[key] = optional_params[key]
        else:
            # New schema (Api-Revision: 2026-05-20):
            # response_mime_type is removed — fold it into response_format.
            response_format = optional_params.get("response_format")
            response_mime_type = optional_params.get("response_mime_type")

            if (
                response_mime_type
                and not isinstance(response_format, list)
                and (
                    not isinstance(response_format, dict)
                    or "mime_type" not in response_format
                )
            ):
                # Wrap the legacy schema into the new polymorphic format.
                new_rf: Dict[str, Any] = {
                    "type": "text",
                    "mime_type": response_mime_type,
                }
                if response_format is not None:
                    new_rf["schema"] = response_format
                response_format = new_rf

            if response_format is not None:
                request_body["response_format"] = response_format

            # image_config moves out of generation_config into response_format.
            generation_config: Optional[Dict[str, Any]] = optional_params.get(
                "generation_config"
            )
            if generation_config is not None:
                image_config = None
                if isinstance(generation_config, dict):
                    generation_config = dict(
                        generation_config
                    )  # avoid mutating the caller's dict
                    image_config = generation_config.pop("image_config", None)
                    if not generation_config:
                        generation_config = None

                if generation_config is not None:
                    request_body["generation_config"] = generation_config

                if image_config is not None:
                    # Move image_config to response_format with type=image.
                    image_rf: Dict[str, Any] = {"type": "image", **image_config}
                    existing_rf = request_body.get("response_format")
                    if existing_rf is None:
                        request_body["response_format"] = image_rf
                    elif isinstance(existing_rf, list):
                        request_body["response_format"] = [*existing_rf, image_rf]
                    else:
                        # Convert single entry to array for multimodal output.
                        request_body["response_format"] = [existing_rf, image_rf]

        return request_body

    def transform_response(
        self,
        model: Optional[str],
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> InteractionsAPIResponse:
        """Parse response - it already matches our response type."""
        try:
            logging_obj.post_call(
                original_response=raw_response.text,
                additional_args={"complete_input_dict": {}},
            )
            raw_json = raw_response.json()
        except Exception:
            raise GeminiError(
                message=raw_response.text,
                status_code=raw_response.status_code,
                headers=dict(raw_response.headers),
            )

        verbose_logger.debug("Google AI Interactions response: %s", raw_json)

        response = InteractionsAPIResponse(**raw_json)
        response._hidden_params["headers"] = dict(raw_response.headers)
        response._hidden_params["additional_headers"] = process_response_headers(
            dict(raw_response.headers)
        )

        return response

    def transform_streaming_response(
        self,
        model: Optional[str],
        parsed_chunk: dict,
        logging_obj: LoveEngineLoggingObj,
    ) -> InteractionsAPIStreamingResponse:
        """Parse streaming chunk."""
        verbose_logger.debug("Google AI Interactions streaming chunk: %s", parsed_chunk)
        return InteractionsAPIStreamingResponse(**parsed_chunk)

    # GET / DELETE / CANCEL - just build URLs, responses match spec directly

    def transform_get_interaction_request(
        self,
        interaction_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """GET /{api_version}/interactions/{interaction_id}"""
        resolved_api_base = GeminiModelInfo.get_api_base(api_base)
        if not GeminiModelInfo.get_api_key(love_engine_params.api_key):
            raise ValueError("Google API key is required")
        encoded_interaction_id = encode_url_path_segment(
            interaction_id, field_name="interaction_id"
        )
        return (
            f"{resolved_api_base}/{self.api_version}/interactions/{encoded_interaction_id}",
            {},
        )

    def transform_get_interaction_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> InteractionsAPIResponse:
        try:
            raw_json = raw_response.json()
        except Exception:
            raise GeminiError(
                message=raw_response.text,
                status_code=raw_response.status_code,
                headers=dict(raw_response.headers),
            )
        response = InteractionsAPIResponse(**raw_json)
        response._hidden_params["headers"] = dict(raw_response.headers)
        return response

    def transform_delete_interaction_request(
        self,
        interaction_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """DELETE /{api_version}/interactions/{interaction_id}"""
        resolved_api_base = GeminiModelInfo.get_api_base(api_base)
        if not GeminiModelInfo.get_api_key(love_engine_params.api_key):
            raise ValueError("Google API key is required")
        encoded_interaction_id = encode_url_path_segment(
            interaction_id, field_name="interaction_id"
        )
        return (
            f"{resolved_api_base}/{self.api_version}/interactions/{encoded_interaction_id}",
            {},
        )

    def transform_delete_interaction_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
        interaction_id: str,
    ) -> DeleteInteractionResult:
        if 200 <= raw_response.status_code < 300:
            return DeleteInteractionResult(success=True, id=interaction_id)
        raise GeminiError(
            message=raw_response.text,
            status_code=raw_response.status_code,
            headers=dict(raw_response.headers),
        )

    def transform_cancel_interaction_request(
        self,
        interaction_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """POST /{api_version}/interactions/{interaction_id}:cancel (if supported)"""
        resolved_api_base = GeminiModelInfo.get_api_base(api_base)
        if not GeminiModelInfo.get_api_key(love_engine_params.api_key):
            raise ValueError("Google API key is required")
        encoded_interaction_id = encode_url_path_segment(
            interaction_id, field_name="interaction_id"
        )
        return (
            f"{resolved_api_base}/{self.api_version}/interactions/{encoded_interaction_id}:cancel",
            {},
        )

    def transform_cancel_interaction_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> CancelInteractionResult:
        try:
            raw_json = raw_response.json()
        except Exception:
            raise GeminiError(
                message=raw_response.text,
                status_code=raw_response.status_code,
                headers=dict(raw_response.headers),
            )
        return CancelInteractionResult(**raw_json)
