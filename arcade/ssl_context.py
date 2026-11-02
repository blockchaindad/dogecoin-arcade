"""Cross-platform SSL context with proper certificate handling.

On Windows, Python's ssl module may not have access to the system certificate store
by default, causing SSL verification failures. This module provides an SSL context
that uses certifi's certificate bundle when available, falling back to the system
default.

Usage:
    from arcade.ssl_context import get_ssl_context, urlopen_with_context

    # Use with urllib
    ctx = get_ssl_context()
    with urllib.request.urlopen(url, context=ctx) as response:
        ...

    # Or use the convenience function
    with urlopen_with_context(url) as response:
        ...
"""
from __future__ import annotations

import ssl
import urllib.request
from typing import Any

_cached_context: ssl.SSLContext | None = None


def get_ssl_context() -> ssl.SSLContext:
    """Get an SSL context with proper certificate handling for all platforms.

    On Windows, this uses certifi's certificate bundle if available.
    Falls back to the system default context if certifi is not installed.
    """
    global _cached_context
    if _cached_context is not None:
        return _cached_context

    ctx = ssl.create_default_context()

    try:
        import certifi
        ctx.load_verify_locations(certifi.where())
    except ImportError:
        pass

    _cached_context = ctx
    return ctx


def urlopen_with_context(url: str | urllib.request.Request, timeout: float = 30, **kwargs: Any):
    """Open a URL with proper SSL context for all platforms.

    This is a convenience wrapper around urllib.request.urlopen that
    automatically uses the correct SSL context.
    """
    ctx = get_ssl_context()
    return urllib.request.urlopen(url, timeout=timeout, context=ctx, **kwargs)
