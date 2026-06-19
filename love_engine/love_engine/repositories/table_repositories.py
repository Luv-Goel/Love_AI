"""
Passthrough table repositories.

Each repository centralizes access to a single Prisma table behind a ``table``
property, making the repository the one place that names the underlying table.
These are thin wrappers for tables that do not (yet) need domain-specific query
methods; richer repositories live in their own modules.
"""

from typing import Any


class PrismaTableRepository:
    """Base for repositories that expose a single Prisma table."""

    table_name: str

    def __init__(self, prisma_client: Any):
        self._prisma_client = prisma_client

    @property
    def prisma_client(self) -> Any:
        if self._prisma_client is None:
            raise RuntimeError(
                "No DB Connected. See - https://docs.love_engine.ai/docs/proxy/virtual_keys"
            )
        return self._prisma_client

    @property
    def table(self) -> Any:
        return getattr(self.prisma_client.db, self.table_name)


class PolicyRepository(PrismaTableRepository):
    table_name = "love_engine_policytable"


class AgentsRepository(PrismaTableRepository):
    table_name = "love_engine_agentstable"


class GuardrailsRepository(PrismaTableRepository):
    table_name = "love_engine_guardrailstable"


class MCPServerRepository(PrismaTableRepository):
    table_name = "love_engine_mcpservertable"


class ManagedObjectRepository(PrismaTableRepository):
    table_name = "love_engine_managedobjecttable"


class OrganizationMembershipRepository(PrismaTableRepository):
    table_name = "love_engine_organizationmembership"


class SpendLogsRepository(PrismaTableRepository):
    table_name = "love_engine_spendlogs"


class ClaudeCodePluginRepository(PrismaTableRepository):
    table_name = "love_engine_claudecodeplugintable"


class TeamMembershipRepository(PrismaTableRepository):
    table_name = "love_engine_teammembership"


class EndUserRepository(PrismaTableRepository):
    table_name = "love_engine_endusertable"


class ManagedVectorStoresRepository(PrismaTableRepository):
    table_name = "love_engine_managedvectorstorestable"


class MCPUserCredentialsRepository(PrismaTableRepository):
    table_name = "love_engine_mcpusercredentials"


class PromptRepository(PrismaTableRepository):
    table_name = "love_engine_prompttable"


class TagRepository(PrismaTableRepository):
    table_name = "love_engine_tagtable"


class InvitationLinkRepository(PrismaTableRepository):
    table_name = "love_engine_invitationlink"


class JWTKeyMappingRepository(PrismaTableRepository):
    table_name = "love_engine_jwtkeymapping"


class ManagedFileRepository(PrismaTableRepository):
    table_name = "love_engine_managedfiletable"


class MemoryRepository(PrismaTableRepository):
    table_name = "love_engine_memorytable"


class SearchToolsRepository(PrismaTableRepository):
    table_name = "love_engine_searchtoolstable"


class ConfigOverridesRepository(PrismaTableRepository):
    table_name = "love_engine_configoverrides"


class MCPToolsetRepository(PrismaTableRepository):
    table_name = "love_engine_mcptoolsettable"


class ToolRepository(PrismaTableRepository):
    table_name = "love_engine_tooltable"


class DeletedVerificationTokenRepository(PrismaTableRepository):
    table_name = "love_engine_deletedverificationtoken"


class WorkflowRunRepository(PrismaTableRepository):
    table_name = "love_engine_workflowrun"


class ModelTableRepository(PrismaTableRepository):
    table_name = "love_engine_modeltable"


class AccessGroupRepository(PrismaTableRepository):
    table_name = "love_engine_accessgrouptable"


class SSOConfigRepository(PrismaTableRepository):
    table_name = "love_engine_ssoconfig"


class UISettingsRepository(PrismaTableRepository):
    table_name = "love_engine_uisettings"


class DailyGuardrailMetricsRepository(PrismaTableRepository):
    table_name = "love_engine_dailyguardrailmetrics"


class PolicyAttachmentRepository(PrismaTableRepository):
    table_name = "love_engine_policyattachmenttable"


class DeletedTeamRepository(PrismaTableRepository):
    table_name = "love_engine_deletedteamtable"


class SkillsRepository(PrismaTableRepository):
    table_name = "love_engine_skillstable"


class CacheConfigRepository(PrismaTableRepository):
    table_name = "love_engine_cacheconfig"


class ManagedVectorStoreIndexRepository(PrismaTableRepository):
    table_name = "love_engine_managedvectorstoreindextable"


class WorkflowMessageRepository(PrismaTableRepository):
    table_name = "love_engine_workflowmessage"


class DailyTagSpendRepository(PrismaTableRepository):
    table_name = "love_engine_dailytagspend"


class SpendLogToolIndexRepository(PrismaTableRepository):
    table_name = "love_engine_spendlogtoolindex"


class SpendLogGuardrailIndexRepository(PrismaTableRepository):
    table_name = "love_engine_spendlogguardrailindex"


class UserNotificationsRepository(PrismaTableRepository):
    table_name = "love_engine_usernotifications"


class HealthCheckRepository(PrismaTableRepository):
    table_name = "love_engine_healthchecktable"


class DeprecatedVerificationTokenRepository(PrismaTableRepository):
    table_name = "love_engine_deprecatedverificationtoken"


class WorkflowEventRepository(PrismaTableRepository):
    table_name = "love_engine_workflowevent"


class DailyPolicyMetricsRepository(PrismaTableRepository):
    table_name = "love_engine_dailypolicymetrics"


class AdaptiveRouterStateRepository(PrismaTableRepository):
    table_name = "love_engine_adaptiverouterstate"


class AuditLogRepository(PrismaTableRepository):
    table_name = "love_engine_auditlog"


class AdaptiveRouterSessionRepository(PrismaTableRepository):
    table_name = "love_engine_adaptiveroutersession"
