"""
New Relic AI Monitoring Integration for love_engine

This module provides integration with New Relic's AI Monitoring feature to track
LLM requests, responses, and usage metrics.
"""

from love_engine.integrations.newrelic.newrelic import NewRelicLogger

__all__ = ["NewRelicLogger"]
