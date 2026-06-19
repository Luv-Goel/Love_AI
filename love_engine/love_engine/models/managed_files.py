"""
Managed file, object, and vector store table models.

Canonical definitions for the ``love_engine_managed*`` tables. Re-exported from
``love_engine.proxy._types`` for backwards compatibility.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from love_engine.types.llms.base import LoveEnginePydanticObjectBase
from love_engine.types.llms.openai import OpenAIFileObject, ResponsesAPIResponse
from love_engine.types.utils import LoveEngineBatch, LoveEngineFineTuningJob


class LOVE_ENGINE_ManagedFileTable(LoveEnginePydanticObjectBase):
    unified_file_id: str
    file_object: Optional[OpenAIFileObject] = None
    model_mappings: Dict[str, str]
    flat_model_file_ids: List[str]
    created_by: Optional[str] = None
    team_id: Optional[str] = None
    updated_by: Optional[str] = None
    storage_backend: Optional[str] = None
    storage_url: Optional[str] = None


class LOVE_ENGINE_ManagedObjectTable(LoveEnginePydanticObjectBase):
    unified_object_id: str
    model_object_id: str
    file_purpose: Literal["batch", "fine-tune", "response", "container"]
    file_object: Union[LoveEngineBatch, LoveEngineFineTuningJob, ResponsesAPIResponse]
    created_by: Optional[str] = None
    team_id: Optional[str] = None


class LOVE_ENGINE_ManagedVectorStoreTable(LoveEnginePydanticObjectBase):
    """Table for managing vector stores with target_model_names support."""

    unified_resource_id: str
    resource_object: Optional[Any] = None
    model_mappings: Dict[str, str]
    flat_model_resource_ids: List[str]
    created_by: Optional[str] = None
    team_id: Optional[str] = None
    updated_by: Optional[str] = None
    storage_backend: Optional[str] = None
    storage_url: Optional[str] = None


class LOVE_ENGINE_ManagedVectorStoresTable(LoveEnginePydanticObjectBase):
    vector_store_id: str
    custom_llm_provider: str
    vector_store_name: Optional[str]
    vector_store_description: Optional[str]
    vector_store_metadata: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    love_engine_credential_name: Optional[str]
    love_engine_params: Optional[Dict[str, Any]]
    team_id: Optional[str]
    user_id: Optional[str]
