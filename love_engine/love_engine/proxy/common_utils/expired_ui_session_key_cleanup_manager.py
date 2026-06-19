"""
Expired UI session key cleanup manager.

Deletes expired virtual keys created for LoveEngine dashboard sessions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from love_engine._logging import verbose_proxy_logger
from love_engine.constants import (
    EXPIRED_UI_SESSION_KEY_CLEANUP_JOB_NAME,
    LOVE_ENGINE_EXPIRED_UI_SESSION_KEY_CLEANUP_BATCH_SIZE,
    LOVE_ENGINE_INTERNAL_JOBS_SERVICE_ACCOUNT_NAME,
    UI_SESSION_TOKEN_TEAM_ID,
)
from love_engine.proxy._types import KeyRequest, LOVE_ENGINE_VerificationToken, UserAPIKeyAuth
from love_engine.proxy.common_utils.user_api_key_cache import UserApiKeyCache
from love_engine.proxy.hooks.key_management_event_hooks import KeyManagementEventHooks
from love_engine.proxy.management_endpoints.key_management_endpoints import (
    delete_verification_tokens,
)
from love_engine.proxy.utils import PrismaClient
from love_engine.repositories.verification_token_repository import (
    VerificationTokenRepository,
)


class ExpiredUISessionKeyCleanupManager:
    """
    Cleans up expired UI session keys.
    """

    def __init__(
        self,
        prisma_client: PrismaClient,
        user_api_key_cache: UserApiKeyCache,
        pod_lock_manager=None,
    ):
        self.prisma_client = prisma_client
        self.user_api_key_cache = user_api_key_cache
        self.pod_lock_manager = pod_lock_manager

    async def cleanup_expired_keys(self) -> int:
        """
        Main entry point for deleting expired UI session keys.
        Uses PodLockManager to ensure only one pod runs cleanup in multi-pod deployments.
        """
        lock_acquired = False
        try:
            if self.pod_lock_manager and self.pod_lock_manager.redis_cache:
                lock_acquired = (
                    await self.pod_lock_manager.acquire_lock(
                        cronjob_id=EXPIRED_UI_SESSION_KEY_CLEANUP_JOB_NAME,
                    )
                    or False
                )
                if not lock_acquired:
                    verbose_proxy_logger.debug(
                        "Expired UI session key cleanup: another pod is already "
                        "running cleanup or Redis lock acquisition failed - "
                        "skipping this cycle."
                    )
                    return 0

            verbose_proxy_logger.info("Starting expired UI session key cleanup...")

            expired_keys = await self._find_expired_ui_session_keys()
            if not expired_keys:
                verbose_proxy_logger.debug("No expired UI session keys found")
                return 0

            tokens = [key.token for key in expired_keys if key.token is not None]
            if not tokens:
                return 0

            system_user = UserAPIKeyAuth.get_love_engine_internal_jobs_user_api_key_auth()
            response, keys_being_deleted = await delete_verification_tokens(
                tokens=tokens,
                user_api_key_cache=self.user_api_key_cache,
                user_api_key_dict=system_user,
                love_engine_changed_by=LOVE_ENGINE_INTERNAL_JOBS_SERVICE_ACCOUNT_NAME,
            )
            await KeyManagementEventHooks.async_key_deleted_hook(
                data=KeyRequest(keys=tokens),
                keys_being_deleted=keys_being_deleted,
                response=response or {},
                user_api_key_dict=system_user,
                love_engine_changed_by=LOVE_ENGINE_INTERNAL_JOBS_SERVICE_ACCOUNT_NAME,
            )
            deleted_count = self._get_deleted_token_count(
                tokens=tokens,
                response=response,
            )
            verbose_proxy_logger.info(
                "Deleted %s expired UI session key(s)", deleted_count
            )
            return deleted_count
        except Exception as e:
            if getattr(e, "status_code", None) == 404:
                verbose_proxy_logger.debug(
                    "Expired UI session key cleanup skipped because selected keys "
                    "were already deleted: %s",
                    e,
                )
                return 0
            verbose_proxy_logger.error(f"Expired UI session key cleanup failed: {e}")
            return 0
        finally:
            if (
                lock_acquired
                and self.pod_lock_manager
                and self.pod_lock_manager.redis_cache
            ):
                await self.pod_lock_manager.release_lock(
                    cronjob_id=EXPIRED_UI_SESSION_KEY_CLEANUP_JOB_NAME,
                )

    @staticmethod
    def _get_deleted_token_count(
        tokens: List[str],
        response: Optional[Dict[str, Any]],
    ) -> int:
        """
        Return the number of tokens actually deleted from the delete helper response.
        """
        if response is None:
            return len(tokens)

        deleted_keys = response.get("deleted_keys")
        if isinstance(deleted_keys, list):
            return len(deleted_keys)
        if isinstance(deleted_keys, int):
            return deleted_keys
        if isinstance(deleted_keys, dict):
            nested_deleted_keys = deleted_keys.get("deleted_keys")
            if isinstance(nested_deleted_keys, list):
                return len(nested_deleted_keys)
            if isinstance(nested_deleted_keys, int):
                return nested_deleted_keys

        failed_tokens = response.get("failed_tokens") or []
        if failed_tokens:
            return max(len(tokens) - len(set(failed_tokens)), 0)

        return len(tokens)

    async def _find_expired_ui_session_keys(self) -> List[LOVE_ENGINE_VerificationToken]:
        """
        Find expired LoveEngine dashboard session keys.
        """
        now = datetime.now(timezone.utc)
        return await VerificationTokenRepository(self.prisma_client).table.find_many(
            where={
                "team_id": UI_SESSION_TOKEN_TEAM_ID,
                "expires": {"lt": now},
            },
            take=LOVE_ENGINE_EXPIRED_UI_SESSION_KEY_CLEANUP_BATCH_SIZE,
        )
