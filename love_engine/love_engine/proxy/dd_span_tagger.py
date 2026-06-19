from typing import Optional

from love_engine._logging import verbose_proxy_logger
from love_engine.love_engine_core_utils.dd_tracing import set_active_span_tag
from love_engine.proxy._types import UserAPIKeyAuth


class DDSpanTagger:
    """Best-effort helpers for tagging the active Datadog APM span with LoveEngine request metadata."""

    @staticmethod
    def tag_call_id(love_engine_call_id: Optional[str]) -> None:
        """
        Attach LoveEngine call id to the active Datadog APM span.

        This enables searching APM traces by LoveEngine call id returned in
        `x-love_engine-call-id`.
        """
        if not love_engine_call_id:
            return
        try:
            set_active_span_tag("love_engine.call_id", str(love_engine_call_id))
        except Exception:
            verbose_proxy_logger.debug(
                "Failed to tag active ddtrace span with love_engine.call_id",
                exc_info=True,
            )

    @staticmethod
    def tag_request(
        user_api_key_dict: UserAPIKeyAuth,
        requested_model: Optional[str],
    ) -> None:
        """
        Attach key and model tags to the active Datadog APM span.

        Tags set (all best-effort, skipped when value is absent):
        - ``love_engine.key_alias``      — human-readable alias for the API key
        - ``love_engine.key_hash``       — hashed API key (safe to log; never the raw secret)
        - ``love_engine.requested_model``— model name as sent by the client

        Use cases:
        - Trace all requests from a specific user/key: filter by ``love_engine.key_alias`` or
          ``love_engine.key_hash``.
        - Trace all requests for a specific model: filter by ``love_engine.requested_model``.

        Note: key_alias / key_hash are not available for unauthenticated (e.g. 401) requests.
        """
        try:
            if user_api_key_dict.key_alias:
                set_active_span_tag(
                    "love_engine.key_alias", str(user_api_key_dict.key_alias)
                )
            if user_api_key_dict.token:
                set_active_span_tag("love_engine.key_hash", str(user_api_key_dict.token))
            if requested_model:
                set_active_span_tag("love_engine.requested_model", str(requested_model))
        except Exception:
            verbose_proxy_logger.debug(
                "Failed to tag active ddtrace span with key/model tags",
                exc_info=True,
            )
