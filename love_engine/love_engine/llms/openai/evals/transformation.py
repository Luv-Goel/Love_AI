"""
OpenAI Evals API configuration and transformations
"""

from typing import Any, Dict, Optional, Tuple

import httpx

from love_engine._logging import verbose_logger
from love_engine.love_engine_core_utils.url_utils import encode_url_path_segment
from love_engine.llms.base_llm.evals.transformation import (
    BaseEvalsAPIConfig,
    LoveEngineLoggingObj,
)
from love_engine.types.llms.openai_evals import (
    CancelEvalResponse,
    CancelRunResponse,
    CreateEvalRequest,
    CreateRunRequest,
    DeleteEvalResponse,
    Eval,
    ListEvalsParams,
    ListEvalsResponse,
    ListRunsParams,
    ListRunsResponse,
    Run,
    RunDeleteResponse,
    UpdateEvalRequest,
)
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import LlmProviders


class OpenAIEvalsConfig(BaseEvalsAPIConfig):
    """OpenAI-specific Evals API configuration"""

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.OPENAI

    def validate_environment(
        self, headers: dict, love_engine_params: Optional[GenericLoveEngineParams]
    ) -> dict:
        """Add OpenAI-specific headers"""
        import love_engine
        from love_engine.secret_managers.main import get_secret_str

        # Get API key following OpenAI pattern
        api_key = None
        if love_engine_params:
            api_key = love_engine_params.api_key

        api_key = (
            api_key
            or love_engine.api_key
            or love_engine.openai_key
            or get_secret_str("OPENAI_API_KEY")
        )

        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for Evals API")

        # Add required headers
        headers["Authorization"] = f"Bearer {api_key}"
        headers["Content-Type"] = "application/json"

        return headers

    def get_complete_url(
        self,
        api_base: Optional[str],
        endpoint: str,
        eval_id: Optional[str] = None,
    ) -> str:
        """Get complete URL for OpenAI Evals API"""
        if api_base is None:
            api_base = "https://api.openai.com"

        if eval_id:
            encoded_eval_id = encode_url_path_segment(eval_id, field_name="eval_id")
            return f"{api_base}/v1/evals/{encoded_eval_id}"
        return f"{api_base}/v1/{endpoint}"

    def transform_create_eval_request(
        self,
        create_request: CreateEvalRequest,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Dict:
        """Transform create eval request for OpenAI"""
        verbose_logger.debug("Transforming create eval request: %s", create_request)

        # OpenAI expects the request body directly
        request_body = {k: v for k, v in create_request.items() if v is not None}

        return request_body

    def transform_create_eval_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Eval:
        """Transform OpenAI response to Eval object"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming create eval response: %s", response_json)

        return Eval(**response_json)

    def transform_list_evals_request(
        self,
        list_params: ListEvalsParams,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform list evals request for OpenAI"""
        api_base = "https://api.openai.com"
        if love_engine_params and love_engine_params.api_base:
            api_base = love_engine_params.api_base

        url = self.get_complete_url(api_base=api_base, endpoint="evals")

        # Build query parameters
        query_params: Dict[str, Any] = {}
        if "limit" in list_params and list_params["limit"]:
            query_params["limit"] = list_params["limit"]
        if "after" in list_params and list_params["after"]:
            query_params["after"] = list_params["after"]
        if "before" in list_params and list_params["before"]:
            query_params["before"] = list_params["before"]
        if "order" in list_params and list_params["order"]:
            query_params["order"] = list_params["order"]
        if "order_by" in list_params and list_params["order_by"]:
            query_params["order_by"] = list_params["order_by"]

        verbose_logger.debug(
            "List evals request made to OpenAI Evals endpoint with params: %s",
            query_params,
        )

        return url, query_params

    def transform_list_evals_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> ListEvalsResponse:
        """Transform OpenAI response to ListEvalsResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming list evals response: %s", response_json)

        return ListEvalsResponse(**response_json)

    def transform_get_eval_request(
        self,
        eval_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform get eval request for OpenAI"""
        url = self.get_complete_url(
            api_base=api_base, endpoint="evals", eval_id=eval_id
        )

        verbose_logger.debug("Get eval request - URL: %s", url)

        return url, headers

    def transform_get_eval_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Eval:
        """Transform OpenAI response to Eval object"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming get eval response: %s", response_json)

        return Eval(**response_json)

    def transform_update_eval_request(
        self,
        eval_id: str,
        update_request: UpdateEvalRequest,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict, Dict]:
        """Transform update eval request for OpenAI"""
        url = self.get_complete_url(
            api_base=api_base, endpoint="evals", eval_id=eval_id
        )

        # Build request body
        request_body = {k: v for k, v in update_request.items() if v is not None}

        verbose_logger.debug(
            "Update eval request - URL: %s, body: %s", url, request_body
        )

        return url, headers, request_body

    def transform_update_eval_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Eval:
        """Transform OpenAI response to Eval object"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming update eval response: %s", response_json)

        return Eval(**response_json)

    def transform_delete_eval_request(
        self,
        eval_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform delete eval request for OpenAI"""
        url = self.get_complete_url(
            api_base=api_base, endpoint="evals", eval_id=eval_id
        )

        verbose_logger.debug("Delete eval request - URL: %s", url)

        return url, headers

    def transform_delete_eval_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> DeleteEvalResponse:
        """Transform OpenAI response to DeleteEvalResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming delete eval response: %s", response_json)

        return DeleteEvalResponse(**response_json)

    def transform_cancel_eval_request(
        self,
        eval_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict, Dict]:
        """Transform cancel eval request for OpenAI"""
        url = f"{self.get_complete_url(api_base=api_base, endpoint='evals', eval_id=eval_id)}/cancel"

        # Empty body for cancel request
        request_body: Dict[str, Any] = {}

        verbose_logger.debug("Cancel eval request - URL: %s", url)

        return url, headers, request_body

    def transform_cancel_eval_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> CancelEvalResponse:
        """Transform OpenAI response to CancelEvalResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming cancel eval response: %s", response_json)

        return CancelEvalResponse(**response_json)

    # Run API Transformations
    def transform_create_run_request(
        self,
        eval_id: str,
        create_request: CreateRunRequest,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform create run request for OpenAI"""
        api_base = "https://api.openai.com"
        if love_engine_params and love_engine_params.api_base:
            api_base = love_engine_params.api_base

        encoded_eval_id = encode_url_path_segment(eval_id, field_name="eval_id")
        url = f"{api_base}/v1/evals/{encoded_eval_id}/runs"

        # Build request body
        request_body = {k: v for k, v in create_request.items() if v is not None}

        verbose_logger.debug(
            "Create run request - URL: %s, body: %s", url, request_body
        )

        return url, request_body

    def transform_create_run_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Run:
        """Transform OpenAI response to Run object"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming create run response: %s", response_json)

        return Run(**response_json)

    def transform_list_runs_request(
        self,
        eval_id: str,
        list_params: ListRunsParams,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform list runs request for OpenAI"""
        api_base = "https://api.openai.com"
        if love_engine_params and love_engine_params.api_base:
            api_base = love_engine_params.api_base

        encoded_eval_id = encode_url_path_segment(eval_id, field_name="eval_id")
        url = f"{api_base}/v1/evals/{encoded_eval_id}/runs"

        # Build query parameters
        query_params: Dict[str, Any] = {}
        if "limit" in list_params and list_params["limit"]:
            query_params["limit"] = list_params["limit"]
        if "after" in list_params and list_params["after"]:
            query_params["after"] = list_params["after"]
        if "before" in list_params and list_params["before"]:
            query_params["before"] = list_params["before"]
        if "order" in list_params and list_params["order"]:
            query_params["order"] = list_params["order"]

        verbose_logger.debug(
            "List runs request made to OpenAI Evals endpoint with params: %s",
            query_params,
        )

        return url, query_params

    def transform_list_runs_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> ListRunsResponse:
        """Transform OpenAI response to ListRunsResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming list runs response: %s", response_json)

        return ListRunsResponse(**response_json)

    def transform_get_run_request(
        self,
        eval_id: str,
        run_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform get run request for OpenAI"""
        encoded_eval_id = encode_url_path_segment(eval_id, field_name="eval_id")
        encoded_run_id = encode_url_path_segment(run_id, field_name="run_id")
        url = f"{api_base}/v1/evals/{encoded_eval_id}/runs/{encoded_run_id}"

        verbose_logger.debug("Get run request - URL: %s", url)

        return url, headers

    def transform_get_run_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Run:
        """Transform OpenAI response to Run object"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming get run response: %s", response_json)

        return Run(**response_json)

    def transform_cancel_run_request(
        self,
        eval_id: str,
        run_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict, Dict]:
        """Transform cancel run request for OpenAI"""
        encoded_eval_id = encode_url_path_segment(eval_id, field_name="eval_id")
        encoded_run_id = encode_url_path_segment(run_id, field_name="run_id")
        url = f"{api_base}/v1/evals/{encoded_eval_id}/runs/{encoded_run_id}/cancel"

        # Empty body for cancel request
        request_body: Dict[str, Any] = {}

        verbose_logger.debug("Cancel run request - URL: %s", url)

        return url, headers, request_body

    def transform_cancel_run_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> CancelRunResponse:
        """Transform OpenAI response to CancelRunResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming cancel run response: %s", response_json)

        return CancelRunResponse(**response_json)

    def transform_delete_run_request(
        self,
        eval_id: str,
        run_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict, Dict]:
        """Transform delete run request for OpenAI"""
        encoded_eval_id = encode_url_path_segment(eval_id, field_name="eval_id")
        encoded_run_id = encode_url_path_segment(run_id, field_name="run_id")
        url = f"{api_base}/v1/evals/{encoded_eval_id}/runs/{encoded_run_id}"

        # Empty body for delete request
        request_body: Dict[str, Any] = {}

        verbose_logger.debug("Delete run request - URL: %s", url)

        return url, headers, request_body

    def transform_delete_run_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> RunDeleteResponse:
        """Transform OpenAI response to RunDeleteResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming delete run response: %s", response_json)

        return RunDeleteResponse(**response_json)
