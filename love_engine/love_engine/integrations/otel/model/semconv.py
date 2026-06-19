"""
Keys follow the OpenTelemetry GenAI semantic conventions (experimental). Anything
without a semconv equivalent lives under the ``love_engine.*`` vendor namespace.
"""

from enum import Enum
from typing import Final


class GenAIOperation(str, Enum):
    """Values for ``gen_ai.operation.name``."""

    CHAT = "chat"
    TEXT_COMPLETION = "text_completion"
    EMBEDDINGS = "embeddings"
    GENERATE_CONTENT = "generate_content"
    CREATE_AGENT = "create_agent"  # reserved for future agent spans
    INVOKE_AGENT = "invoke_agent"  # reserved for future agent spans
    EXECUTE_TOOL = "execute_tool"  # MCP tool-call spans


class GenAIProvider(str, Enum):
    """Common values for the ``gen_ai.provider.name`` attribute."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AWS_BEDROCK = "aws.bedrock"
    AZURE_AI_OPENAI = "azure.ai.openai"
    AZURE_AI_INFERENCE = "azure.ai.inference"
    GCP_GEMINI = "gcp.gemini"
    GCP_VERTEX_AI = "gcp.vertex_ai"
    COHERE = "cohere"
    MISTRAL_AI = "mistral_ai"
    DEEPSEEK = "deepseek"
    GROQ = "groq"
    PERPLEXITY = "perplexity"
    X_AI = "x_ai"
    IBM_WATSONX_AI = "ibm.watsonx.ai"


class MCPMethod(str, Enum):
    """Well-known values for ``mcp.method.name`` that love_engine's MCP gateway
    serves. The value is the JSON-RPC method exactly as it travels on the wire."""

    TOOLS_CALL = "tools/call"
    TOOLS_LIST = "tools/list"
    PROMPTS_GET = "prompts/get"
    PROMPTS_LIST = "prompts/list"


class GenAI:
    """Canonical OTel GenAI span-attribute keys."""

    # request
    OPERATION_NAME: Final = "gen_ai.operation.name"
    PROVIDER_NAME: Final = "gen_ai.provider.name"
    REQUEST_MODEL: Final = "gen_ai.request.model"
    REQUEST_TEMPERATURE: Final = "gen_ai.request.temperature"
    REQUEST_TOP_P: Final = "gen_ai.request.top_p"
    REQUEST_TOP_K: Final = "gen_ai.request.top_k"
    REQUEST_MAX_TOKENS: Final = "gen_ai.request.max_tokens"
    REQUEST_FREQUENCY_PENALTY: Final = "gen_ai.request.frequency_penalty"
    REQUEST_PRESENCE_PENALTY: Final = "gen_ai.request.presence_penalty"
    REQUEST_STOP_SEQUENCES: Final = "gen_ai.request.stop_sequences"
    REQUEST_SEED: Final = "gen_ai.request.seed"
    REQUEST_CHOICE_COUNT: Final = "gen_ai.request.choice.count"
    REQUEST_ENCODING_FORMATS: Final = "gen_ai.request.encoding_formats"
    # response
    RESPONSE_ID: Final = "gen_ai.response.id"
    RESPONSE_MODEL: Final = "gen_ai.response.model"
    RESPONSE_FINISH_REASONS: Final = "gen_ai.response.finish_reasons"
    # usage
    USAGE_INPUT_TOKENS: Final = "gen_ai.usage.input_tokens"
    USAGE_OUTPUT_TOKENS: Final = "gen_ai.usage.output_tokens"
    # content (opt-in, gated by capture mode)
    INPUT_MESSAGES: Final = "gen_ai.input.messages"
    OUTPUT_MESSAGES: Final = "gen_ai.output.messages"
    SYSTEM_INSTRUCTIONS: Final = "gen_ai.system_instructions"
    OUTPUT_TYPE: Final = "gen_ai.output.type"
    CONVERSATION_ID: Final = "gen_ai.conversation.id"
    # agent (reserved)
    AGENT_ID: Final = "gen_ai.agent.id"
    AGENT_NAME: Final = "gen_ai.agent.name"
    # tool / tool-call (stamped on MCP tool-call spans). Arguments and result are
    # the tool's input/output payloads — sensitive, so they're opt-in and gated by
    # the same content-capture mode as prompt/response content.
    TOOL_NAME: Final = "gen_ai.tool.name"
    TOOL_CALL_ID: Final = "gen_ai.tool.call.id"
    TOOL_CALL_ARGUMENTS: Final = "gen_ai.tool.call.arguments"
    TOOL_CALL_RESULT: Final = "gen_ai.tool.call.result"
    # prompt (MCP ``prompts/get`` etc.)
    PROMPT_NAME: Final = "gen_ai.prompt.name"


class MCP:
    """OTel GenAI MCP (Model Context Protocol) span-attribute keys.

    ``METHOD_NAME`` is the only key love_engine populates from a closed request today;
    the rest are part of the convention's vocabulary and are stamped when the
    corresponding signal (session, protocol version, resource) is available.
    """

    METHOD_NAME: Final = "mcp.method.name"
    SESSION_ID: Final = "mcp.session.id"
    PROTOCOL_VERSION: Final = "mcp.protocol.version"
    RESOURCE_URI: Final = "mcp.resource.uri"


class JsonRpc:
    """JSON-RPC keys carried on MCP spans. The error/status code lives in the
    ``rpc.*`` namespace per semconv, not ``jsonrpc.*``."""

    REQUEST_ID: Final = "jsonrpc.request.id"
    PROTOCOL_VERSION: Final = "jsonrpc.protocol.version"
    RESPONSE_STATUS_CODE: Final = "rpc.response.status_code"


class NetworkTransport(str, Enum):
    """Well-known values for ``network.transport``."""

    TCP = "tcp"
    UDP = "udp"
    QUIC = "quic"
    UNIX = "unix"
    PIPE = "pipe"


class Network:
    """OTel network keys, recommended on MCP spans to describe the transport
    carrying the JSON-RPC messages (stdio pipe, HTTP, websocket, …)."""

    PROTOCOL_NAME: Final = "network.protocol.name"
    PROTOCOL_VERSION: Final = "network.protocol.version"
    TRANSPORT: Final = "network.transport"


class Client:
    """Peer (client) network keys, stamped on MCP *server* spans the same way
    ``server.*`` is stamped on client spans."""

    ADDRESS: Final = "client.address"
    PORT: Final = "client.port"


class Error:
    TYPE: Final = "error.type"


class ExceptionEvent:
    """OTel exception-event name and attribute keys (semconv ``exception.*``).

    The full error message rides ``exception.message`` on a span event rather than
    a custom string attribute. Backends recognise these semantic-convention names
    and map them as full text; an unrecognised key (e.g. ``error_message``) falls
    into the default dynamic template, which truncates strings to a 1024-char
    ``keyword``.
    """

    NAME: Final = "exception"
    TYPE: Final = "exception.type"
    MESSAGE: Final = "exception.message"


class Server:
    ADDRESS: Final = "server.address"
    PORT: Final = "server.port"


class DB:
    """Database / cache client-span keys (OTel ``db.*`` semconv).

    Stamped on ``DB_CALL`` spans (redis / postgres), which are CLIENT spans for
    outbound datastore calls — not on the INTERNAL ``SERVICE`` spans.
    """

    SYSTEM_NAME: Final = "db.system.name"
    OPERATION_NAME: Final = "db.operation.name"


class HTTP:
    """HTTP server-span keys. Belong on the SERVER span only (never promoted)."""

    REQUEST_METHOD: Final = "http.request.method"
    ROUTE: Final = "http.route"
    RESPONSE_STATUS_CODE: Final = "http.response.status_code"
    URL_PATH: Final = "url.path"


class love_engine:
    """Vendor-extension keys (no semconv equivalent). Always ``love_engine.*``."""

    CALL_ID: Final = "love_engine.call_id"
    COST_PREFIX: Final = "love_engine.cost."
    METADATA_PREFIX: Final = "love_engine.metadata."
    TEAM_ID: Final = "love_engine.team.id"
    TEAM_ALIAS: Final = "love_engine.team.alias"
    # The team's free-form metadata dict, JSON-serialized into a single value.
    TEAM_METADATA: Final = "love_engine.team.metadata"
    KEY_HASH: Final = "love_engine.api_key.hash"
    END_USER: Final = "love_engine.end_user.id"
    # The model string love_engine actually sent to the provider (the deployment's
    # ``love_engine_params.model``), distinct from the user-facing ``gen_ai.request.model``.
    PROVIDER_MODEL: Final = "love_engine.provider.model"
    REQUEST_STREAMING: Final = "love_engine.request.streaming"
    GUARDRAIL_NAME: Final = "love_engine.guardrail.name"
    GUARDRAIL_MODE: Final = "love_engine.guardrail.mode"
    GUARDRAIL_STATUS: Final = "love_engine.guardrail.status"
    GUARDRAIL_PROVIDER: Final = "love_engine.guardrail.provider"
    GUARDRAIL_ACTION: Final = "love_engine.guardrail.action"
    GUARDRAIL_RESPONSE: Final = "love_engine.guardrail.response"
    GUARDRAIL_VIOLATION_CATEGORIES: Final = "love_engine.guardrail.violation_categories"
    GUARDRAIL_CONFIDENCE_SCORE: Final = "love_engine.guardrail.confidence_score"
    GUARDRAIL_RISK_SCORE: Final = "love_engine.guardrail.risk_score"
    GUARDRAIL_MASKED_ENTITY_COUNT: Final = "love_engine.guardrail.masked_entity_count"
    GUARDRAIL_DURATION: Final = "love_engine.guardrail.duration"
    GUARDRAIL_ID: Final = "love_engine.guardrail.id"
    GUARDRAIL_POLICY_TEMPLATE: Final = "love_engine.guardrail.policy_template"
    GUARDRAIL_DETECTION_METHOD: Final = "love_engine.guardrail.detection_method"
    SERVICE_NAME: Final = "love_engine.service.name"
    SERVICE_CALL_TYPE: Final = "love_engine.service.call_type"
    PREPROCESSING_MS: Final = "love_engine.preprocessing.duration_ms"
    # The logical name of the MCP server a tool call was routed to. There is no
    # semconv key for an MCP server's *name* (the convention uses ``server.address``
    # for its network location), so it lives under the vendor namespace.
    MCP_SERVER_NAME: Final = "love_engine.mcp.server.name"


class Metric:
    """GenAI metric instrument names."""

    TOKEN_USAGE: Final = "gen_ai.client.token.usage"
    OPERATION_DURATION: Final = "gen_ai.client.operation.duration"
    TOKEN_COST: Final = "gen_ai.client.token.cost"
    TIME_TO_FIRST_TOKEN: Final = "gen_ai.client.response.time_to_first_token"
    TIME_PER_OUTPUT_TOKEN: Final = "gen_ai.client.response.time_per_output_token"
    RESPONSE_DURATION: Final = "gen_ai.client.response.duration"


# love_engine ``custom_llm_provider`` -> ``gen_ai.provider.name`` value.
_PROVIDER_BY_LoveEngine: dict[str, GenAIProvider] = {
    "openai": GenAIProvider.OPENAI,
    "text-completion-openai": GenAIProvider.OPENAI,
    "azure": GenAIProvider.AZURE_AI_OPENAI,
    "azure_ai": GenAIProvider.AZURE_AI_INFERENCE,
    "anthropic": GenAIProvider.ANTHROPIC,
    "bedrock": GenAIProvider.AWS_BEDROCK,
    "bedrock_converse": GenAIProvider.AWS_BEDROCK,
    "vertex_ai": GenAIProvider.GCP_VERTEX_AI,
    "vertex_ai_beta": GenAIProvider.GCP_VERTEX_AI,
    "gemini": GenAIProvider.GCP_GEMINI,
    "cohere": GenAIProvider.COHERE,
    "cohere_chat": GenAIProvider.COHERE,
    "mistral": GenAIProvider.MISTRAL_AI,
    "deepseek": GenAIProvider.DEEPSEEK,
    "groq": GenAIProvider.GROQ,
    "perplexity": GenAIProvider.PERPLEXITY,
    "xai": GenAIProvider.X_AI,
    "watsonx": GenAIProvider.IBM_WATSONX_AI,
}

# love_engine ``call_type`` -> ``gen_ai.operation.name``.
_OPERATION_BY_CALL_TYPE: dict[str, GenAIOperation] = {
    "completion": GenAIOperation.CHAT,
    "acompletion": GenAIOperation.CHAT,
    "completion_with_retries": GenAIOperation.CHAT,
    "text_completion": GenAIOperation.TEXT_COMPLETION,
    "atext_completion": GenAIOperation.TEXT_COMPLETION,
    "embedding": GenAIOperation.EMBEDDINGS,
    "aembedding": GenAIOperation.EMBEDDINGS,
    "responses": GenAIOperation.CHAT,
    "aresponses": GenAIOperation.CHAT,
    "call_mcp_tool": GenAIOperation.EXECUTE_TOOL,
}


def resolve_provider(custom_llm_provider: str | None) -> str:
    """Map a love_engine provider string to a ``gen_ai.provider.name`` value.

    Unknown providers pass through verbatim — the convention explicitly allows
    provider-specific values, so an unmapped name is still valid.
    """
    if not custom_llm_provider:
        return ""
    mapped = _PROVIDER_BY_LoveEngine.get(custom_llm_provider.lower())
    return mapped.value if mapped is not None else custom_llm_provider


def resolve_operation(call_type: str | None) -> GenAIOperation:
    """Map a love_engine ``call_type`` to a ``gen_ai.operation.name`` value."""
    if not call_type:
        return GenAIOperation.CHAT
    return _OPERATION_BY_CALL_TYPE.get(call_type.lower(), GenAIOperation.CHAT)
