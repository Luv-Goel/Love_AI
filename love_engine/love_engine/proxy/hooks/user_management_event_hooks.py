"""
Hooks that are triggered when a love_engine user event occurs
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel

import love_engine
from love_engine._logging import verbose_proxy_logger
from love_engine._uuid import uuid
from love_engine.proxy._types import (
    AUDIT_ACTIONS,
    CommonProxyErrors,
    LOVE_ENGINE_AuditLogs,
    LOVE_ENGINE_EntityType,
    LOVE_ENGINE_UserTable,
    LoveEngineTableNames,
    NewUserRequest,
    NewUserResponse,
    UserAPIKeyAuth,
    WebhookEvent,
)
from love_engine.proxy.management_helpers.audit_logs import create_audit_log_for_update
from love_engine.repositories.user_repository import UserRepository


class UserManagementEventHooks:
    @staticmethod
    async def async_user_created_hook(
        data: NewUserRequest,
        response: NewUserResponse,
        user_api_key_dict: UserAPIKeyAuth,
    ):
        """
        This hook is called when a new user is created on love_engine

        Handles:
        - Creating an audit log for the user creation
        - Sending a user invitation email to the user
        """
        from love_engine.proxy.proxy_server import love_engine_proxy_admin_name, prisma_client

        #########################################################
        ########## Send User Invitation Email ################
        #########################################################
        await UserManagementEventHooks.async_send_user_invitation_email(
            data=data,
            response=response,
            user_api_key_dict=user_api_key_dict,
        )

        #########################################################
        ########## CREATE AUDIT LOG ################
        #########################################################
        try:
            if prisma_client is None:
                raise Exception(CommonProxyErrors.db_not_connected_error.value)
            user_row: BaseModel = await UserRepository(prisma_client).table.find_first(
                where={"user_id": response.user_id}
            )

            user_row_love_engine_typed = LOVE_ENGINE_UserTable(
                **user_row.model_dump(exclude_none=True)
            )
            asyncio.create_task(
                UserManagementEventHooks.create_internal_user_audit_log(
                    user_id=user_row_love_engine_typed.user_id,
                    action="created",
                    love_engine_changed_by=user_api_key_dict.user_id,
                    user_api_key_dict=user_api_key_dict,
                    love_engine_proxy_admin_name=love_engine_proxy_admin_name,
                    before_value=None,
                    after_value=user_row_love_engine_typed.model_dump_json(
                        exclude_none=True
                    ),
                )
            )
        except Exception as e:
            verbose_proxy_logger.warning(
                "Unable to create audit log for user on `/user/new` - {}".format(str(e))
            )
        pass

    @staticmethod
    async def async_send_user_invitation_email(
        data: NewUserRequest,
        response: NewUserResponse,
        user_api_key_dict: UserAPIKeyAuth,
    ):
        """
        Send a user invitation email to the user
        """
        event = WebhookEvent(
            event="internal_user_created",
            event_group=LOVE_ENGINE_EntityType.USER,
            event_message="Welcome to LoveEngine Proxy",
            token=response.token,
            spend=response.spend or 0.0,
            max_budget=response.max_budget,
            user_id=response.user_id,
            user_email=response.user_email,
            team_id=response.team_id,
            key_alias=response.key_alias,
        )

        #########################################################
        ########## V2 USER INVITATION EMAIL ################
        #########################################################
        try:
            from love_engine_enterprise.enterprise_callbacks.send_emails.base_email import (
                BaseEmailLogger,
            )

            use_enterprise_email_hooks = True
        except ImportError:
            verbose_proxy_logger.warning(
                "Defaulting to using Legacy Email Hooks."
                + CommonProxyErrors.missing_enterprise_package.value
            )
            use_enterprise_email_hooks = False

        if use_enterprise_email_hooks and (data.send_invite_email is True):
            initialized_email_loggers = love_engine.logging_callback_manager.get_custom_loggers_for_type(
                callback_type=BaseEmailLogger  # type: ignore
            )
            if len(initialized_email_loggers) > 0:
                for email_logger in initialized_email_loggers:
                    if isinstance(email_logger, BaseEmailLogger):  # type: ignore
                        await email_logger.send_user_invitation_email(  # type: ignore
                            event=event,
                        )

        #########################################################
        ########## LEGACY V1 USER INVITATION EMAIL ################
        #########################################################
        if data.send_invite_email is True:
            await UserManagementEventHooks.send_legacy_v1_user_invitation_email(
                data=data,
                response=response,
                user_api_key_dict=user_api_key_dict,
                event=event,
            )

    @staticmethod
    async def send_legacy_v1_user_invitation_email(
        data: NewUserRequest,
        response: NewUserResponse,
        user_api_key_dict: UserAPIKeyAuth,
        event: WebhookEvent,
    ):
        """
        Send a user invitation email to the user
        """
        from love_engine.proxy.proxy_server import general_settings, proxy_logging_obj

        # check if user has setup email alerting
        if "email" not in general_settings.get("alerting", []):
            raise ValueError(
                "Email alerting not setup on config.yaml. Please set `alerting=['email']. \nDocs: https://docs.love_engine.ai/docs/proxy/email`"
            )

        # If user configured email alerting - send an Email letting their end-user know the key was created
        asyncio.create_task(
            proxy_logging_obj.slack_alerting_instance.send_key_created_or_user_invited_email(
                webhook_event=event,
            )
        )

    @staticmethod
    async def create_internal_user_audit_log(
        user_id: str,
        action: AUDIT_ACTIONS,
        love_engine_changed_by: Optional[str],
        user_api_key_dict: UserAPIKeyAuth,
        love_engine_proxy_admin_name: Optional[str],
        before_value: Optional[str] = None,
        after_value: Optional[str] = None,
    ):
        """
        Create an audit log for an internal user.

        Parameters:
        - user_id: str - The id of the user to create the audit log for.
        - action: AUDIT_ACTIONS - The action to create the audit log for.
        - user_row: LOVE_ENGINE_UserTable - The user row to create the audit log for.
        - love_engine_changed_by: Optional[str] - The user id of the user who is changing the user.
        - user_api_key_dict: UserAPIKeyAuth - The user api key dictionary.
        - love_engine_proxy_admin_name: Optional[str] - The name of the proxy admin.
        """
        if not love_engine.store_audit_logs:
            return

        from love_engine.proxy.management_helpers.audit_logs import (
            get_audit_log_changed_by,
        )

        await create_audit_log_for_update(
            request_data=LOVE_ENGINE_AuditLogs(
                id=str(uuid.uuid4()),
                updated_at=datetime.now(timezone.utc),
                changed_by=get_audit_log_changed_by(
                    love_engine_changed_by=love_engine_changed_by,
                    user_api_key_dict=user_api_key_dict,
                    love_engine_proxy_admin_name=love_engine_proxy_admin_name,
                ),
                changed_by_api_key=user_api_key_dict.api_key,
                table_name=LoveEngineTableNames.USER_TABLE_NAME,
                object_id=user_id,
                action=action,
                updated_values=after_value,
                before_value=before_value,
            )
        )
