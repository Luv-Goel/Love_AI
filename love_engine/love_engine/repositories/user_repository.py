"""
User repository for database operations on LOVE_ENGINE_UserTable.
"""

import json
from typing import Any, Dict, List, Optional, Type

from love_engine.models.user import LOVE_ENGINE_UserTable
from love_engine.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[LOVE_ENGINE_UserTable]):
    """Repository for user database operations."""

    @property
    def table(self) -> Any:
        return self.prisma_client.db.love_engine_usertable

    @property
    def model_class(self) -> Type[LOVE_ENGINE_UserTable]:
        return LOVE_ENGINE_UserTable

    def _to_model(self, record: Any) -> Optional[LOVE_ENGINE_UserTable]:
        """Convert a database record to a User model."""
        if record is None:
            return None

        data = record.dict() if hasattr(record, "dict") else dict(record)

        json_fields = ["metadata", "model_spend", "model_max_budget"]
        for field in json_fields:
            if isinstance(data.get(field), str):
                data[field] = json.loads(data[field])

        return LOVE_ENGINE_UserTable(**data)

    async def find_by_id(
        self, user_id: str, id_field: str = "user_id"
    ) -> Optional[LOVE_ENGINE_UserTable]:
        return await super().find_by_id(user_id, id_field)

    async def find_by_email(self, user_email: str) -> Optional[LOVE_ENGINE_UserTable]:
        """Find a user by email."""
        records = await self.table.find_many(where={"user_email": user_email})
        if records:
            return self._to_model(records[0])
        return None

    async def find_by_sso_id(self, sso_user_id: str) -> Optional[LOVE_ENGINE_UserTable]:
        """Find a user by SSO ID."""
        record = await self.table.find_unique(where={"sso_user_id": sso_user_id})
        return self._to_model(record)

    async def find_by_organization_id(
        self, organization_id: str
    ) -> List[LOVE_ENGINE_UserTable]:
        """Find all users in an organization."""
        records = await self.table.find_many(where={"organization_id": organization_id})
        return self._to_model_list(records)

    async def find_by_team_id(self, team_id: str) -> List[LOVE_ENGINE_UserTable]:
        """Find all users in a team."""
        records = await self.table.find_many(where={"teams": {"has": team_id}})
        return self._to_model_list(records)

    async def create_user(
        self,
        user_id: str,
        user_alias: Optional[str] = None,
        team_id: Optional[str] = None,
        sso_user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        password: Optional[str] = None,
        teams: Optional[List[str]] = None,
        user_role: Optional[str] = None,
        max_budget: Optional[float] = None,
        user_email: Optional[str] = None,
        models: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_parallel_requests: Optional[int] = None,
        tpm_limit: Optional[int] = None,
        rpm_limit: Optional[int] = None,
        budget_duration: Optional[str] = None,
        allowed_cache_controls: Optional[List[str]] = None,
        policies: Optional[List[str]] = None,
        object_permission_id: Optional[str] = None,
    ) -> LOVE_ENGINE_UserTable:
        """Create a new user."""
        data: Dict[str, Any] = {"user_id": user_id}
        if user_alias is not None:
            data["user_alias"] = user_alias
        if team_id is not None:
            data["team_id"] = team_id
        if sso_user_id is not None:
            data["sso_user_id"] = sso_user_id
        if organization_id is not None:
            data["organization_id"] = organization_id
        if password is not None:
            data["password"] = password
        if teams is not None:
            data["teams"] = teams
        if user_role is not None:
            data["user_role"] = user_role
        if max_budget is not None:
            data["max_budget"] = max_budget
        if user_email is not None:
            data["user_email"] = user_email
        if models is not None:
            data["models"] = models
        if metadata is not None:
            data["metadata"] = json.dumps(metadata)
        if max_parallel_requests is not None:
            data["max_parallel_requests"] = max_parallel_requests
        if tpm_limit is not None:
            data["tpm_limit"] = tpm_limit
        if rpm_limit is not None:
            data["rpm_limit"] = rpm_limit
        if budget_duration is not None:
            data["budget_duration"] = budget_duration
        if allowed_cache_controls is not None:
            data["allowed_cache_controls"] = allowed_cache_controls
        if policies is not None:
            data["policies"] = policies
        if object_permission_id is not None:
            data["object_permission_id"] = object_permission_id

        return await self.create(data)

    async def update_user(
        self,
        user_id: str,
        user_alias: Optional[str] = None,
        team_id: Optional[str] = None,
        sso_user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        password: Optional[str] = None,
        teams: Optional[List[str]] = None,
        user_role: Optional[str] = None,
        max_budget: Optional[float] = None,
        user_email: Optional[str] = None,
        models: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_parallel_requests: Optional[int] = None,
        tpm_limit: Optional[int] = None,
        rpm_limit: Optional[int] = None,
        budget_duration: Optional[str] = None,
        allowed_cache_controls: Optional[List[str]] = None,
        policies: Optional[List[str]] = None,
        object_permission_id: Optional[str] = None,
    ) -> Optional[LOVE_ENGINE_UserTable]:
        """Update a user."""
        data: Dict[str, Any] = {}
        if user_alias is not None:
            data["user_alias"] = user_alias
        if team_id is not None:
            data["team_id"] = team_id
        if sso_user_id is not None:
            data["sso_user_id"] = sso_user_id
        if organization_id is not None:
            data["organization_id"] = organization_id
        if password is not None:
            data["password"] = password
        if teams is not None:
            data["teams"] = teams
        if user_role is not None:
            data["user_role"] = user_role
        if max_budget is not None:
            data["max_budget"] = max_budget
        if user_email is not None:
            data["user_email"] = user_email
        if models is not None:
            data["models"] = models
        if metadata is not None:
            data["metadata"] = json.dumps(metadata)
        if max_parallel_requests is not None:
            data["max_parallel_requests"] = max_parallel_requests
        if tpm_limit is not None:
            data["tpm_limit"] = tpm_limit
        if rpm_limit is not None:
            data["rpm_limit"] = rpm_limit
        if budget_duration is not None:
            data["budget_duration"] = budget_duration
        if allowed_cache_controls is not None:
            data["allowed_cache_controls"] = allowed_cache_controls
        if policies is not None:
            data["policies"] = policies
        if object_permission_id is not None:
            data["object_permission_id"] = object_permission_id

        return await self.update(user_id, data, id_field="user_id")

    async def delete_user(self, user_id: str) -> Optional[LOVE_ENGINE_UserTable]:
        """Delete a user."""
        return await self.delete(user_id, id_field="user_id")

    async def update_spend(
        self, user_id: str, spend: float
    ) -> Optional[LOVE_ENGINE_UserTable]:
        """Update user spend."""
        return await self.update(user_id, {"spend": spend}, id_field="user_id")

    async def add_to_team(
        self, user_id: str, team_id: str
    ) -> Optional[LOVE_ENGINE_UserTable]:
        """Add a user to a team using atomic array push operation."""
        if not await self.exists(user_id, id_field="user_id"):
            return None

        record = await self.table.update(
            where={"user_id": user_id},
            data={"teams": {"push": team_id}},
        )
        return self._to_model(record)

    async def remove_from_team(
        self, user_id: str, team_id: str
    ) -> Optional[LOVE_ENGINE_UserTable]:
        """Remove a user from a team.

        Note: Prisma doesn't support atomic array removal, so we use a
        read-modify-write pattern here. For high-concurrency scenarios,
        consider using raw SQL with array_remove().
        """
        user = await self.find_by_id(user_id)
        if user is None:
            return None

        teams = [t for t in user.teams if t != team_id]
        return await self.update(user_id, {"teams": teams}, id_field="user_id")
