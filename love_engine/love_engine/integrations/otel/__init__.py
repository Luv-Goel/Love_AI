"""Typed, semconv-aligned OpenTelemetry instrumentation for love_engine.

The three sources of truth — attribute keys (:mod:`semconv`), the span and
hierarchy registry (:mod:`spans`), and the typed span-data inputs
(:mod:`payloads`) — plus :mod:`config` are exported here and are free of any
``opentelemetry`` import. The engine layer (``emitter``, ``providers``,
``context``, ``metrics``) and the ``CustomLogger`` adapter (``logger``) are
reached via their submodule paths so that importing this package never
requires the OTel SDK.

The ``LOVE_ENGINE_OTEL_V2`` env var gates whether the factory in
``love_engine_core_utils.love_engine_logging`` constructs the ``OpenTelemetryV2``
class (from :mod:`logger`).
"""

from love_engine.integrations.otel.model.config import (
    OTEL_V2_ENV,
    OpenTelemetryV2Config,
    is_otel_v2_enabled,
)
from love_engine.integrations.otel.model.baggage import (
    BAGGAGE_PROMOTED_KEYS,
    DEFAULT_BAGGAGE_METADATA_KEYS,
    promoted_baggage,
)
from love_engine.integrations.otel.model.metadata import (
    RequestContext,
    RequestIdentity,
)
from love_engine.integrations.otel.model.payloads import (
    GuardrailSpanData,
    LLMCallSpanData,
    LLMRequestParams,
    LLMUsage,
    MCPToolCallSpanData,
    ProxyRequestSpanData,
    ServerInfo,
    ServiceSpanData,
    SpanError,
    is_mcp_tool_call,
)
from love_engine.integrations.otel.model.semconv import (
    DB,
    HTTP,
    MCP,
    Client,
    Error,
    GenAI,
    GenAIOperation,
    GenAIProvider,
    JsonRpc,
    love_engine,
    MCPMethod,
    Metric,
    Network,
    NetworkTransport,
    Server,
    resolve_operation,
    resolve_provider,
)
from love_engine.integrations.otel.model.spans import (
    SPAN_REGISTRY,
    LoveEngineSpanKind,
    SpanRole,
    SpanSpec,
    db_system,
    span_role_for_service,
    validate_registry,
)

__all__ = [
    # config
    "OTEL_V2_ENV",
    "OpenTelemetryV2Config",
    "is_otel_v2_enabled",
    # semconv
    "BAGGAGE_PROMOTED_KEYS",
    "DB",
    "DEFAULT_BAGGAGE_METADATA_KEYS",
    "Client",
    "Error",
    "GenAI",
    "GenAIOperation",
    "GenAIProvider",
    "HTTP",
    "JsonRpc",
    "love_engine",
    "MCP",
    "MCPMethod",
    "Metric",
    "Network",
    "NetworkTransport",
    "Server",
    "resolve_operation",
    "resolve_provider",
    # spans
    "SPAN_REGISTRY",
    "LoveEngineSpanKind",
    "SpanRole",
    "SpanSpec",
    "db_system",
    "span_role_for_service",
    "validate_registry",
    # payloads
    "GuardrailSpanData",
    "LLMCallSpanData",
    "LLMRequestParams",
    "LLMUsage",
    "MCPToolCallSpanData",
    "ProxyRequestSpanData",
    "RequestContext",
    "RequestIdentity",
    "ServerInfo",
    "ServiceSpanData",
    "SpanError",
    "is_mcp_tool_call",
    "promoted_baggage",
]
