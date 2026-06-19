from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from love_engine.love_engine_core_utils.url_utils import encode_url_path_segment
from love_engine.llms.openai.vector_stores.transformation import OpenAIVectorStoreConfig
from love_engine.secret_managers.main import get_secret_str
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.vector_stores import VectorStoreSearchOptionalRequestParams

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
else:
    LoveEngineLoggingObj = Any


class PGVectorStoreConfig(OpenAIVectorStoreConfig):
    """
    PG Vector Store configuration that inherits from OpenAI since it's OpenAI-compatible.

    love_engine Provides an OpenAI Compatible Server to connect to PG Vector.

    https://github.com/BerriAI/love_engine-pgvector

    You just need to connect love_engine proxy to this deployed server.

    Requires:
    - api_base: The base URL for the PG vector service
    - api_key: API key for authentication with the PG vector service
    """

    def validate_environment(
        self, headers: dict, love_engine_params: Optional[GenericLoveEngineParams]
    ) -> dict:
        """
        Validate environment and set headers for PG vector service authentication
        """
        love_engine_params = love_engine_params or GenericLoveEngineParams()

        # Get API key from various sources
        api_key = love_engine_params.api_key or get_secret_str("PG_VECTOR_API_KEY")

        if not api_key:
            raise ValueError(
                "PG Vector API key is required. Set PG_VECTOR_API_KEY environment variable or pass api_key in love_engine_params."
            )

        headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

        return headers

    def get_complete_url(
        self,
        api_base: Optional[str],
        love_engine_params: dict,
    ) -> str:
        """
        Get the complete URL for PG vector service endpoints
        """
        # Get API base from various sources
        api_base = api_base or get_secret_str("PG_VECTOR_API_BASE")

        if not api_base:
            raise ValueError(
                "PG Vector API base URL is required. Set PG_VECTOR_API_BASE environment variable or pass api_base in love_engine_params."
            )

        # Remove trailing slashes
        api_base = api_base.rstrip("/")

        return f"{api_base}/v1/vector_stores"

    def transform_search_vector_store_request(
        self,
        vector_store_id: str,
        query: Union[str, List[str]],
        vector_store_search_optional_params: VectorStoreSearchOptionalRequestParams,
        api_base: str,
        love_engine_logging_obj: LoveEngineLoggingObj,
        love_engine_params: dict,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict]:
        encoded_vector_store_id = encode_url_path_segment(
            vector_store_id, field_name="vector_store_id"
        )
        url = f"{api_base}/{encoded_vector_store_id}/search"
        _, request_body = super().transform_search_vector_store_request(
            vector_store_id=vector_store_id,
            query=query,
            vector_store_search_optional_params=vector_store_search_optional_params,
            api_base=api_base,
            love_engine_logging_obj=love_engine_logging_obj,
            love_engine_params=love_engine_params,
            extra_body=extra_body,
        )
        return url, request_body
