from datetime import datetime, timezone

import love_engine
from love_engine.love_engine_core_utils.duration_parser import get_next_standardized_reset_time


def get_budget_reset_timezone():
    """
    Get the budget reset timezone from love_engine_settings.
    Falls back to UTC if not specified.

    love_engine_settings values are set as attributes on the love_engine module
    by proxy_server.py at startup (via setattr(love_engine, key, value)).
    """
    return getattr(love_engine, "timezone", None) or "UTC"


def get_budget_reset_time(budget_duration: str) -> datetime:
    """
    Get the budget reset time based on the configured timezone.
    Falls back to UTC if not specified.
    """

    reset_at = get_next_standardized_reset_time(
        duration=budget_duration,
        current_time=datetime.now(timezone.utc),
        timezone_str=get_budget_reset_timezone(),
    )
    return reset_at
