"""
Anthropic Skills API configuration and transformations
"""

from typing import Any, Dict, Optional, Tuple

import httpx

from love_engine._logging import verbose_logger
from love_engine.love_engine_core_utils.url_utils import encode_url_path_segment
from love_engine.llms.base_llm.skills.transformation import (
    BaseSkillsAPIConfig,
    LoveEngineLoggingObj,
)
from love_engine.types.llms.anthropic_skills import (
    CreateSkillRequest,
    DeleteSkillResponse,
    ListSkillsParams,
    ListSkillsResponse,
    Skill,
)
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import LlmProviders


class AnthropicSkillsConfig(BaseSkillsAPIConfig):
    """Anthropic-specific Skills API configuration"""

    @property
    def custom_llm_provider(self) -> LlmProviders:
        return LlmProviders.ANTHROPIC

    def validate_environment(
        self, headers: dict, love_engine_params: Optional[GenericLoveEngineParams]
    ) -> dict:
        """Add Anthropic-specific headers"""
        from love_engine.llms.anthropic.common_utils import AnthropicModelInfo

        # Get API key from love_engine_params if available
        api_key = None
        if love_engine_params is not None:
            api_key = love_engine_params.api_key

        auth_header = AnthropicModelInfo.get_auth_header(api_key)
        if auth_header is None:
            raise ValueError(
                "ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN is required for Skills API"
            )

        headers.update(auth_header)
        headers["anthropic-version"] = "2023-06-01"

        # Add beta header for skills API
        from love_engine.constants import ANTHROPIC_SKILLS_API_BETA_VERSION

        if "anthropic-beta" not in headers:
            headers["anthropic-beta"] = ANTHROPIC_SKILLS_API_BETA_VERSION
        elif isinstance(headers["anthropic-beta"], list):
            if ANTHROPIC_SKILLS_API_BETA_VERSION not in headers["anthropic-beta"]:
                headers["anthropic-beta"].append(ANTHROPIC_SKILLS_API_BETA_VERSION)
        elif isinstance(headers["anthropic-beta"], str):
            if ANTHROPIC_SKILLS_API_BETA_VERSION not in headers["anthropic-beta"]:
                headers["anthropic-beta"] = [
                    headers["anthropic-beta"],
                    ANTHROPIC_SKILLS_API_BETA_VERSION,
                ]

        headers["content-type"] = "application/json"

        return headers

    def get_complete_url(
        self,
        api_base: Optional[str],
        endpoint: str,
        skill_id: Optional[str] = None,
    ) -> str:
        """Get complete URL for Anthropic Skills API"""
        from love_engine.llms.anthropic.common_utils import AnthropicModelInfo

        if api_base is None:
            api_base = AnthropicModelInfo.get_api_base()

        if skill_id:
            encoded_skill_id = encode_url_path_segment(skill_id, field_name="skill_id")
            return f"{api_base}/v1/skills/{encoded_skill_id}"
        return f"{api_base}/v1/{endpoint}"

    def transform_create_skill_request(
        self,
        create_request: CreateSkillRequest,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Dict:
        """Transform create skill request for Anthropic"""
        verbose_logger.debug("Transforming create skill request: %s", create_request)

        # Anthropic expects the request body directly
        request_body = {k: v for k, v in create_request.items() if v is not None}

        return request_body

    def transform_create_skill_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Skill:
        """Transform Anthropic response to Skill object"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming create skill response: %s", response_json)

        return Skill(**response_json)

    def transform_list_skills_request(
        self,
        list_params: ListSkillsParams,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform list skills request for Anthropic"""
        from love_engine.llms.anthropic.common_utils import AnthropicModelInfo

        api_base = AnthropicModelInfo.get_api_base(
            love_engine_params.api_base if love_engine_params else None
        )
        url = self.get_complete_url(api_base=api_base, endpoint="skills")

        # Build query parameters
        query_params: Dict[str, Any] = {}
        if "limit" in list_params and list_params["limit"]:
            query_params["limit"] = list_params["limit"]
        if "page" in list_params and list_params["page"]:
            query_params["page"] = list_params["page"]
        if "source" in list_params and list_params["source"]:
            query_params["source"] = list_params["source"]

        verbose_logger.debug(
            "List skills request made to Anthropic Skills endpoint with params: %s",
            query_params,
        )

        return url, query_params

    def transform_list_skills_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> ListSkillsResponse:
        """Transform Anthropic response to ListSkillsResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming list skills response: %s", response_json)

        return ListSkillsResponse(**response_json)

    def transform_get_skill_request(
        self,
        skill_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform get skill request for Anthropic"""
        url = self.get_complete_url(
            api_base=api_base, endpoint="skills", skill_id=skill_id
        )

        verbose_logger.debug("Get skill request - URL: %s", url)

        return url, headers

    def transform_get_skill_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Skill:
        """Transform Anthropic response to Skill object"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming get skill response: %s", response_json)

        return Skill(**response_json)

    def transform_delete_skill_request(
        self,
        skill_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """Transform delete skill request for Anthropic"""
        url = self.get_complete_url(
            api_base=api_base, endpoint="skills", skill_id=skill_id
        )

        verbose_logger.debug("Delete skill request - URL: %s", url)

        return url, headers

    def transform_delete_skill_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> DeleteSkillResponse:
        """Transform Anthropic response to DeleteSkillResponse"""
        response_json = raw_response.json()
        verbose_logger.debug("Transforming delete skill response: %s", response_json)

        return DeleteSkillResponse(**response_json)
