import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

import httpx

from love_engine.llms.base_llm.vector_store.transformation import BaseVectorStoreConfig
from love_engine.llms.bedrock.base_aws_llm import BaseAWSLLM
from love_engine.types.router import GenericLoveEngineParams
from love_engine.types.vector_stores import (
    VECTOR_STORE_OPENAI_PARAMS,
    BaseVectorStoreAuthCredentials,
    VectorStoreIndexEndpoints,
    VectorStoreResultContent,
    VectorStoreSearchOptionalRequestParams,
    VectorStoreSearchResponse,
    VectorStoreSearchResult,
)

if TYPE_CHECKING:
    from love_engine.love_engine_core_utils.love_engine_logging import Logging as LoveEngineLoggingObj
else:
    LoveEngineLoggingObj = Any


class S3VectorsVectorStoreConfig(BaseVectorStoreConfig, BaseAWSLLM):
    """Vector store configuration for AWS S3 Vectors."""

    def __init__(self) -> None:
        BaseVectorStoreConfig.__init__(self)
        BaseAWSLLM.__init__(self)

    def get_auth_credentials(
        self, love_engine_params: dict
    ) -> BaseVectorStoreAuthCredentials:
        return {}

    def get_vector_store_endpoints_by_type(self) -> VectorStoreIndexEndpoints:
        return {
            "read": [("POST", "/QueryVectors")],
            "write": [],
        }

    def get_supported_openai_params(
        self, model: str
    ) -> List[VECTOR_STORE_OPENAI_PARAMS]:
        return ["max_num_results"]

    def map_openai_params(
        self,
        non_default_params: dict,
        optional_params: dict,
        drop_params: bool,
    ) -> dict:
        for param, value in non_default_params.items():
            if param == "max_num_results":
                optional_params["maxResults"] = value
        return optional_params

    def validate_environment(
        self, headers: dict, love_engine_params: Optional[GenericLoveEngineParams]
    ) -> dict:
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
        return headers

    def get_complete_url(self, api_base: Optional[str], love_engine_params: dict) -> str:
        aws_region_name = love_engine_params.get("aws_region_name")
        if not aws_region_name:
            raise ValueError("aws_region_name is required for S3 Vectors")
        if not re.match(r"^[a-z][a-z0-9-]*$", aws_region_name):
            raise ValueError("Invalid aws_region_name format")
        return f"https://s3vectors.{aws_region_name}.api.aws"

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
        """Sync version - generates embedding synchronously."""
        # For S3 Vectors, vector_store_id should be in format: bucket_name:index_name
        # If not in that format, try to construct it from love_engine_params
        bucket_name: str
        index_name: str

        if ":" in vector_store_id:
            bucket_name, index_name = vector_store_id.split(":", 1)
        else:
            # Try to get bucket_name from love_engine_params
            bucket_name_from_params = love_engine_params.get("vector_bucket_name")
            if not bucket_name_from_params or not isinstance(
                bucket_name_from_params, str
            ):
                raise ValueError(
                    "vector_store_id must be in format 'bucket_name:index_name' for S3 Vectors, "
                    "or vector_bucket_name must be provided in love_engine_params"
                )
            bucket_name = bucket_name_from_params
            index_name = vector_store_id

        if isinstance(query, list):
            query = " ".join(query)

        # Generate embedding for the query
        embedding_model = love_engine_params.get(
            "embedding_model", "text-embedding-3-small"
        )

        import love_engine as love_engine_module

        embedding_response = love_engine_module.embedding(
            model=embedding_model, input=[query]
        )
        query_embedding = embedding_response.data[0]["embedding"]

        url = f"{api_base}/QueryVectors"

        request_body: Dict[str, Any] = {
            "vectorBucketName": bucket_name,
            "indexName": index_name,
            "queryVector": {"float32": query_embedding},
            "topK": vector_store_search_optional_params.get(
                "max_num_results", 5
            ),  # Default to 5
            "returnDistance": True,
            "returnMetadata": True,
        }

        love_engine_logging_obj.model_call_details["query"] = query
        return url, request_body

    async def atransform_search_vector_store_request(
        self,
        vector_store_id: str,
        query: Union[str, List[str]],
        vector_store_search_optional_params: VectorStoreSearchOptionalRequestParams,
        api_base: str,
        love_engine_logging_obj: LoveEngineLoggingObj,
        love_engine_params: dict,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict]:
        """Async version - generates embedding asynchronously."""
        # For S3 Vectors, vector_store_id should be in format: bucket_name:index_name
        # If not in that format, try to construct it from love_engine_params
        bucket_name: str
        index_name: str

        if ":" in vector_store_id:
            bucket_name, index_name = vector_store_id.split(":", 1)
        else:
            # Try to get bucket_name from love_engine_params
            bucket_name_from_params = love_engine_params.get("vector_bucket_name")
            if not bucket_name_from_params or not isinstance(
                bucket_name_from_params, str
            ):
                raise ValueError(
                    "vector_store_id must be in format 'bucket_name:index_name' for S3 Vectors, "
                    "or vector_bucket_name must be provided in love_engine_params"
                )
            bucket_name = bucket_name_from_params
            index_name = vector_store_id

        if isinstance(query, list):
            query = " ".join(query)

        # Generate embedding for the query asynchronously
        embedding_model = love_engine_params.get(
            "embedding_model", "text-embedding-3-small"
        )

        import love_engine as love_engine_module

        embedding_response = await love_engine_module.aembedding(
            model=embedding_model, input=[query]
        )
        query_embedding = embedding_response.data[0]["embedding"]

        url = f"{api_base}/QueryVectors"

        request_body: Dict[str, Any] = {
            "vectorBucketName": bucket_name,
            "indexName": index_name,
            "queryVector": {"float32": query_embedding},
            "topK": vector_store_search_optional_params.get(
                "max_num_results", 5
            ),  # Default to 5
            "returnDistance": True,
            "returnMetadata": True,
        }

        love_engine_logging_obj.model_call_details["query"] = query
        return url, request_body

    def sign_request(
        self,
        headers: dict,
        optional_params: Dict,
        request_data: Dict,
        api_base: str,
        api_key: Optional[str] = None,
    ) -> Tuple[dict, Optional[bytes]]:
        return self._sign_request(
            service_name="s3vectors",
            headers=headers,
            optional_params=optional_params,
            request_data=request_data,
            api_base=api_base,
            api_key=api_key,
        )

    def transform_search_vector_store_response(
        self, response: httpx.Response, love_engine_logging_obj: LoveEngineLoggingObj
    ) -> VectorStoreSearchResponse:
        try:
            response_data = response.json()
            results: List[VectorStoreSearchResult] = []

            for item in response_data.get("vectors", []) or []:
                metadata = item.get("metadata", {}) or {}
                source_text = metadata.get("source_text", "")

                if not source_text:
                    continue

                # Extract file information from metadata
                chunk_index = metadata.get("chunk_index", "0")
                file_id = f"s3-vectors-chunk-{chunk_index}"
                filename = metadata.get("filename", f"document-{chunk_index}")

                # S3 Vectors returns distance, convert to similarity score (0-1)
                # Lower distance = higher similarity
                # We'll normalize using 1 / (1 + distance) to get a 0-1 score
                distance = item.get("distance")
                score = None
                if distance is not None:
                    # Convert distance to similarity score between 0 and 1
                    # For cosine distance: similarity = 1 - distance
                    # For euclidean: use 1 / (1 + distance)
                    # Assuming cosine distance here
                    score = max(0.0, min(1.0, 1.0 - float(distance)))

                results.append(
                    VectorStoreSearchResult(
                        score=score,
                        content=[
                            VectorStoreResultContent(text=source_text, type="text")
                        ],
                        file_id=file_id,
                        filename=filename,
                        attributes=metadata,
                    )
                )

            return VectorStoreSearchResponse(
                object="vector_store.search_results.page",
                search_query=love_engine_logging_obj.model_call_details.get("query", ""),
                data=results,
            )
        except Exception as e:
            raise self.get_error_class(
                error_message=str(e),
                status_code=response.status_code,
                headers=response.headers,
            )

    # Vector store creation is not yet implemented
    def transform_create_vector_store_request(
        self,
        vector_store_create_optional_params,
        api_base: str,
    ) -> Tuple[str, Dict]:
        raise NotImplementedError

    def transform_create_vector_store_response(self, response: httpx.Response):
        raise NotImplementedError
