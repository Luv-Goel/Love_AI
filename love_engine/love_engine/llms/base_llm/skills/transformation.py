"""
Base configuration class for Skills API
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

import httpx

from love_engine.llms.base_llm.chat.transformation import BaseLLMException
from love_engine.types.llms.anthropic_skills import (
    CreateSkillRequest,
    DeleteSkillResponse,
    ListSkillsParams,
    ListSkillsResponse,
    Skill,
)
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.utils import LlmProviders

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as _LoveEngineLoggingObj

    LoveEngineLoggingObj = _LoveEngineLoggingObj
else:
    LoveEngineLoggingObj = Any


class BaseSkillsAPIConfig(ABC):
    """Base configuration for Skills API providers"""

    def __init__(self):
        pass

    @property
    @abstractmethod
    def custom_llm_provider(self) -> LlmProviders:
        pass

    @abstractmethod
    def validate_environment(
        self, headers: dict, love_engine_params: Optional[GenericLoveEngineParams]
    ) -> dict:
        """
        Validate and update headers with provider-specific requirements

        Args:
            headers: Base headers dictionary
            love_engine_params: love_engine parameters

        Returns:
            Updated headers dictionary
        """
        return headers

    @abstractmethod
    def get_complete_url(
        self,
        api_base: Optional[str],
        endpoint: str,
        skill_id: Optional[str] = None,
    ) -> str:
        """
        Get the complete URL for the API request

        Args:
            api_base: Base API URL
            endpoint: API endpoint (e.g., 'skills', 'skills/{id}')
            skill_id: Optional skill ID for specific skill operations

        Returns:
            Complete URL
        """
        if api_base is None:
            raise ValueError("api_base is required")
        return f"{api_base}/v1/{endpoint}"

    @abstractmethod
    def transform_create_skill_request(
        self,
        create_request: CreateSkillRequest,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Dict:
        """
        Transform create skill request to provider-specific format

        Args:
            create_request: Skill creation parameters
            love_engine_params: love_engine parameters
            headers: Request headers

        Returns:
            Provider-specific request body
        """
        pass

    @abstractmethod
    def transform_create_skill_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Skill:
        """
        Transform provider response to Skill object

        Args:
            raw_response: Raw HTTP response
            logging_obj: Logging object

        Returns:
            Skill object
        """
        pass

    @abstractmethod
    def transform_list_skills_request(
        self,
        list_params: ListSkillsParams,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """
        Transform list skills request parameters

        Args:
            list_params: List parameters (pagination, filters)
            love_engine_params: love_engine parameters
            headers: Request headers

        Returns:
            Tuple of (url, query_params)
        """
        pass

    @abstractmethod
    def transform_list_skills_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> ListSkillsResponse:
        """
        Transform provider response to ListSkillsResponse

        Args:
            raw_response: Raw HTTP response
            logging_obj: Logging object

        Returns:
            ListSkillsResponse object
        """
        pass

    @abstractmethod
    def transform_get_skill_request(
        self,
        skill_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """
        Transform get skill request

        Args:
            skill_id: Skill ID
            api_base: Base API URL
            love_engine_params: love_engine parameters
            headers: Request headers

        Returns:
            Tuple of (url, headers)
        """
        pass

    @abstractmethod
    def transform_get_skill_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> Skill:
        """
        Transform provider response to Skill object

        Args:
            raw_response: Raw HTTP response
            logging_obj: Logging object

        Returns:
            Skill object
        """
        pass

    @abstractmethod
    def transform_delete_skill_request(
        self,
        skill_id: str,
        api_base: str,
        love_engine_params: GenericLoveEngineParams,
        headers: dict,
    ) -> Tuple[str, Dict]:
        """
        Transform delete skill request

        Args:
            skill_id: Skill ID
            api_base: Base API URL
            love_engine_params: love_engine parameters
            headers: Request headers

        Returns:
            Tuple of (url, headers)
        """
        pass

    @abstractmethod
    def transform_delete_skill_response(
        self,
        raw_response: httpx.Response,
        logging_obj: LoveEngineLoggingObj,
    ) -> DeleteSkillResponse:
        """
        Transform provider response to DeleteSkillResponse

        Args:
            raw_response: Raw HTTP response
            logging_obj: Logging object

        Returns:
            DeleteSkillResponse object
        """
        pass

    def get_error_class(
        self,
        error_message: str,
        status_code: int,
        headers: dict,
    ) -> Exception:
        """Get appropriate error class for the provider."""
        return BaseLLMException(
            status_code=status_code,
            message=error_message,
            headers=headers,
        )
