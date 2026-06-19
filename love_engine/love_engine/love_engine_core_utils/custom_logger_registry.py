"""
Registry mapping the callback class string to the class type.

This is used to get the class type from the callback class string.

Example:
    "datadog" -> DataDogLogger
    "prometheus" -> PrometheusLogger
"""

from typing import Union

from love_engine import _custom_logger_compatible_callbacks_literal
from love_engine.integrations.agentops import AgentOps
from love_engine.integrations.anthropic_cache_control_hook import AnthropicCacheControlHook
from love_engine.integrations.argilla import ArgillaLogger
from love_engine.integrations.azure_sentinel.azure_sentinel import AzureSentinelLogger
from love_engine.integrations.azure_storage.azure_storage import AzureBlobStorageLogger
from love_engine.integrations.bitbucket import BitBucketPromptManager
from love_engine.integrations.braintrust_logging import BraintrustLogger
from love_engine.integrations.cloudzero.cloudzero import CloudZeroLogger
from love_engine.integrations.datadog.datadog import DataDogLogger
from love_engine.integrations.datadog.datadog_llm_obs import DataDogLLMObsLogger
from love_engine.integrations.datadog.datadog_metrics import DatadogMetricsLogger
from love_engine.integrations.deepeval import DeepEvalLogger
from love_engine.integrations.dotprompt import DotpromptManager
from love_engine.integrations.focus.focus_logger import FocusLogger
from love_engine.integrations.mavvrik_focus.mavvrik_focus_logger import MavvrikFocusLogger
from love_engine.integrations.vantage.vantage_logger import VantageLogger
from love_engine.integrations.galileo import GalileoObserve
from love_engine.integrations.gcs_bucket.gcs_bucket import GCSBucketLogger
from love_engine.integrations.gcs_pubsub.pub_sub import GcsPubSubLogger
from love_engine.integrations.gitlab import GitLabPromptManager
from love_engine.integrations.humanloop import HumanloopLogger
from love_engine.integrations.lago import LagoLogger
from love_engine.integrations.langfuse.langfuse_prompt_management import (
    LangfusePromptManagement,
)
from love_engine.integrations.langsmith import LangsmithLogger
from love_engine.integrations.love_engine_agent import LoveEngineAgentModelResolver
from love_engine.integrations.literal_ai import LiteralAILogger
from love_engine.integrations.mlflow import MlflowLogger
from love_engine.integrations.newrelic import NewRelicLogger
from love_engine.integrations.openmeter import OpenMeterLogger
from love_engine.integrations.opentelemetry import OpenTelemetry
from love_engine.integrations.opik.opik import OpikLogger
from love_engine.integrations.posthog import PostHogLogger
from love_engine.integrations.prometheus import PrometheusLogger
from love_engine.integrations.s3_v2 import S3Logger
from love_engine.integrations.sqs import SQSLogger
from love_engine.integrations.vector_store_integrations.vector_store_pre_call_hook import (
    VectorStorePreCallHook,
)
from love_engine.proxy.hooks.dynamic_rate_limiter import _PROXY_DynamicRateLimitHandler
from love_engine.proxy.hooks.dynamic_rate_limiter_v3 import _PROXY_DynamicRateLimitHandlerV3


class CustomLoggerRegistry:
    """
    Registry mapping the callback class string to the class type.
    """

    CALLBACK_CLASS_STR_TO_CLASS_TYPE = {
        "lago": LagoLogger,
        "openmeter": OpenMeterLogger,
        "braintrust": BraintrustLogger,
        "galileo": GalileoObserve,
        "langsmith": LangsmithLogger,
        "literalai": LiteralAILogger,
        "love_engine_agent": LoveEngineAgentModelResolver,
        "prometheus": PrometheusLogger,
        "datadog": DataDogLogger,
        "datadog_llm_observability": DataDogLLMObsLogger,
        "datadog_metrics": DatadogMetricsLogger,
        "gcs_bucket": GCSBucketLogger,
        "opik": OpikLogger,
        "argilla": ArgillaLogger,
        "opentelemetry": OpenTelemetry,
        "azure_sentinel": AzureSentinelLogger,
        "azure_storage": AzureBlobStorageLogger,
        "humanloop": HumanloopLogger,
        # OTEL compatible loggers
        "logfire": OpenTelemetry,
        "arize": OpenTelemetry,
        "langfuse_otel": OpenTelemetry,
        "arize_phoenix": OpenTelemetry,
        "langtrace": OpenTelemetry,
        "weave_otel": OpenTelemetry,
        "levo": OpenTelemetry,
        "mlflow": MlflowLogger,
        "langfuse": LangfusePromptManagement,
        "otel": OpenTelemetry,
        "gcs_pubsub": GcsPubSubLogger,
        "anthropic_cache_control_hook": AnthropicCacheControlHook,
        "agentops": AgentOps,
        "deepeval": DeepEvalLogger,
        "s3_v2": S3Logger,
        "aws_sqs": SQSLogger,
        "dynamic_rate_limiter": _PROXY_DynamicRateLimitHandler,
        "dynamic_rate_limiter_v3": _PROXY_DynamicRateLimitHandlerV3,
        "vector_store_pre_call_hook": VectorStorePreCallHook,
        "dotprompt": DotpromptManager,
        "bitbucket": BitBucketPromptManager,
        "gitlab": GitLabPromptManager,
        "cloudzero": CloudZeroLogger,
        "focus": FocusLogger,
        "mavvrik": MavvrikFocusLogger,
        "vantage": VantageLogger,
        "posthog": PostHogLogger,
        "newrelic": NewRelicLogger,
    }

    try:
        from love_engine_enterprise.enterprise_callbacks.pagerduty.pagerduty import (
            PagerDutyAlerting,
        )
        from love_engine_enterprise.enterprise_callbacks.send_emails.resend_email import (
            ResendEmailLogger,
        )
        from love_engine_enterprise.enterprise_callbacks.send_emails.sendgrid_email import (
            SendGridEmailLogger,
        )
        from love_engine_enterprise.enterprise_callbacks.send_emails.smtp_email import (
            SMTPEmailLogger,
        )

        from love_engine.integrations.generic_api.generic_api_callback import (
            GenericAPILogger,
        )

        enterprise_loggers = {
            "pagerduty": PagerDutyAlerting,
            "generic_api": GenericAPILogger,
            "resend_email": ResendEmailLogger,
            "sendgrid_email": SendGridEmailLogger,
            "smtp_email": SMTPEmailLogger,
        }
        CALLBACK_CLASS_STR_TO_CLASS_TYPE.update(enterprise_loggers)
    except ImportError:
        pass  # enterprise not installed

    @classmethod
    def get_callback_str_from_class_type(cls, class_type: type) -> Union[str, None]:
        """
        Get the callback string from the class type.

        Args:
            class_type: The class type to find the string for

        Returns:
            str: The callback string, or None if not found
        """
        for (
            callback_str,
            callback_class,
        ) in cls.CALLBACK_CLASS_STR_TO_CLASS_TYPE.items():
            if callback_class == class_type:
                return callback_str
        return None

    @classmethod
    def get_all_callback_strs_from_class_type(cls, class_type: type) -> list[str]:
        """
        Get all callback strings that map to the same class type.
        Some class types (like OpenTelemetry) have multiple string mappings.

        Args:
            class_type: The class type to find all strings for

        Returns:
            list: List of callback strings that map to the class type
        """
        callback_strs: list[str] = []
        for (
            callback_str,
            callback_class,
        ) in cls.CALLBACK_CLASS_STR_TO_CLASS_TYPE.items():
            if callback_class == class_type:
                callback_strs.append(callback_str)
        return callback_strs

    @classmethod
    def get_class_type_for_custom_logger_name(
        cls,
        custom_logger_name: _custom_logger_compatible_callbacks_literal,
    ) -> type:
        """
        Get the class type for a given custom logger name
        """
        return cls.CALLBACK_CLASS_STR_TO_CLASS_TYPE[custom_logger_name]
