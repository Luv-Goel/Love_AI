"""
Model repository for database operations on LOVE_ENGINE_ProxyModelTable.
"""

import json
from typing import Any, Dict, List, Optional, Type

from love_engine.models.model import LOVE_ENGINE_ProxyModelTable
from love_engine.repositories.base_repository import BaseRepository
from love_engine.proxy.common_utils.encrypt_decrypt_utils import (
    decrypt_value_helper,
    encrypt_value_helper,
)


class ModelRepository(BaseRepository[LOVE_ENGINE_ProxyModelTable]):
    """Repository for proxy model database operations with encryption support."""

    def __init__(self, prisma_client: Any, encryption_key: Optional[str] = None):
        super().__init__(prisma_client)
        self._encryption_key = encryption_key

    @property
    def table(self) -> Any:
        return self.prisma_client.db.love_engine_proxymodeltable

    @property
    def model_class(self) -> Type[LOVE_ENGINE_ProxyModelTable]:
        return LOVE_ENGINE_ProxyModelTable

    def _encrypt_love_engine_params(self, love_engine_params: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive values in love_engine_params."""
        encrypted = {}
        for key, value in love_engine_params.items():
            if isinstance(value, str):
                encrypted[key] = encrypt_value_helper(
                    value, new_encryption_key=self._encryption_key
                )
            else:
                encrypted[key] = value
        return encrypted

    def _decrypt_love_engine_params(self, love_engine_params: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive values in love_engine_params."""
        decrypted = {}
        for key, value in love_engine_params.items():
            if isinstance(value, str):
                decrypted[key] = decrypt_value_helper(
                    value, key=key, exception_type="debug", return_original_value=True
                )
            else:
                decrypted[key] = value
        return decrypted

    def _to_model(self, record: Any) -> Optional[LOVE_ENGINE_ProxyModelTable]:
        """Convert a database record to a Model with decryption."""
        if record is None:
            return None

        data = record.dict() if hasattr(record, "dict") else dict(record)

        if isinstance(data.get("love_engine_params"), str):
            data["love_engine_params"] = json.loads(data["love_engine_params"])
        if isinstance(data.get("model_info"), str):
            data["model_info"] = json.loads(data["model_info"])

        if data.get("love_engine_params"):
            data["love_engine_params"] = self._decrypt_love_engine_params(
                data["love_engine_params"]
            )

        return LOVE_ENGINE_ProxyModelTable(**data)

    async def find_by_id(
        self, model_id: str, id_field: str = "model_id"
    ) -> Optional[LOVE_ENGINE_ProxyModelTable]:
        return await super().find_by_id(model_id, id_field)

    async def find_by_name(self, model_name: str) -> List[LOVE_ENGINE_ProxyModelTable]:
        """Find models by name."""
        records = await self.table.find_many(where={"model_name": model_name})
        return self._to_model_list(records)

    async def find_all(self) -> List[LOVE_ENGINE_ProxyModelTable]:
        """Find all models."""
        records = await self.table.find_many()
        return self._to_model_list(records)

    async def find_unblocked(self) -> List[LOVE_ENGINE_ProxyModelTable]:
        """Find all models that are not blocked."""
        records = await self.table.find_many(where={"blocked": False})
        return self._to_model_list(records)

    async def find_by_team_id(self, team_id: str) -> List[LOVE_ENGINE_ProxyModelTable]:
        """Find models associated with a specific team.

        Note: This filters in-memory since team_id is stored within love_engine_params
        JSON. For large deployments with many models, consider adding a dedicated
        team_id column with a database index.
        """
        all_models = await self.find_all()
        return [m for m in all_models if m.team_id == team_id]

    async def create_model(
        self,
        model_name: str,
        love_engine_params: Dict[str, Any],
        created_by: str,
        model_id: Optional[str] = None,
        model_info: Optional[Dict[str, Any]] = None,
        blocked: bool = False,
    ) -> LOVE_ENGINE_ProxyModelTable:
        """Create a new model with encryption."""
        encrypted_params = self._encrypt_love_engine_params(love_engine_params)

        data: Dict[str, Any] = {
            "model_name": model_name,
            "love_engine_params": json.dumps(encrypted_params),
            "created_by": created_by,
            "updated_by": created_by,
            "blocked": blocked,
        }
        if model_id is not None:
            data["model_id"] = model_id
        if model_info is not None:
            data["model_info"] = json.dumps(model_info)

        record = await self.table.create(data=data)
        model = self._to_model(record)
        assert model is not None
        return model

    async def update_model(
        self,
        model_id: str,
        updated_by: str,
        model_name: Optional[str] = None,
        love_engine_params: Optional[Dict[str, Any]] = None,
        model_info: Optional[Dict[str, Any]] = None,
        blocked: Optional[bool] = None,
    ) -> Optional[LOVE_ENGINE_ProxyModelTable]:
        """Update a model with encryption."""
        data: Dict[str, Any] = {"updated_by": updated_by}
        if model_name is not None:
            data["model_name"] = model_name
        if love_engine_params is not None:
            encrypted_params = self._encrypt_love_engine_params(love_engine_params)
            data["love_engine_params"] = json.dumps(encrypted_params)
        if model_info is not None:
            data["model_info"] = json.dumps(model_info)
        if blocked is not None:
            data["blocked"] = blocked

        record = await self.table.update(where={"model_id": model_id}, data=data)
        return self._to_model(record)

    async def delete_model(self, model_id: str) -> Optional[LOVE_ENGINE_ProxyModelTable]:
        """Delete a model."""
        return await self.delete(model_id, id_field="model_id")

    async def block_model(
        self, model_id: str, updated_by: str
    ) -> Optional[LOVE_ENGINE_ProxyModelTable]:
        """Block a model."""
        return await self.update_model(model_id, updated_by, blocked=True)

    async def unblock_model(
        self, model_id: str, updated_by: str
    ) -> Optional[LOVE_ENGINE_ProxyModelTable]:
        """Unblock a model."""
        return await self.update_model(model_id, updated_by, blocked=False)
