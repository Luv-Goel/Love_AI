"""
Proxy Authentication module for LoveEngine SDK.

This module provides OAuth2/JWT token management for authenticating
with LoveEngine Proxy or any OAuth2-protected endpoint.

Usage:
    from love_engine.proxy_auth import AzureADCredential, ProxyAuthHandler

    love_engine.proxy_auth = ProxyAuthHandler(
        credential=AzureADCredential(),
        scope="api://my-proxy/.default"
    )
"""

from .credentials import (
    AccessToken,
    TokenCredential,
    AzureADCredential,
    GenericOAuth2Credential,
    ProxyAuthHandler,
)

__all__ = [
    "AccessToken",
    "TokenCredential",
    "AzureADCredential",
    "GenericOAuth2Credential",
    "ProxyAuthHandler",
]
