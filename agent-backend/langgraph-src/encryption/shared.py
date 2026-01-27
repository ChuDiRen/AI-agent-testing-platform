"""Shared encryption constants and utilities.

This module contains constants and helper functions used by both
custom encryption (via SDK) and built-in AES encryption.
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langgraph_api.encryption.aes_json import AesEncryptionInstance
    from langgraph_api.encryption.custom import JsonEncryptionWrapper

# Marker keys for encryption context storage
ENCRYPTION_CONTEXT_KEY = "__encryption_context__"
BLOB_ENCRYPTION_CONTEXT_KEY = "__blob_encryption_context__"

# Reserved keys that should never appear in user-facing responses
RESERVED_ENCRYPTION_KEYS = frozenset(
    {ENCRYPTION_CONTEXT_KEY, BLOB_ENCRYPTION_CONTEXT_KEY}
)


def strip_encryption_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Strip encryption-related keys from a data dict.

    Used during decryption to remove internal markers before returning
    data to callers.

    Args:
        data: Dict that may contain encryption marker keys

    Returns:
        New dict with marker keys removed
    """
    return {k: v for k, v in data.items() if k not in RESERVED_ENCRYPTION_KEYS}


@functools.lru_cache(maxsize=1)
def get_encryption() -> JsonEncryptionWrapper | AesEncryptionInstance | None:
    """Get the effective encryption instance for JSON encryption.

    Returns the cached encryption instance based on configuration:
    - Custom + AES configured: JsonEncryptionWrapper (handles migration)
    - AES only: AesEncryptionInstance
    - Neither: None
    """
    # Late import to avoid circular dependency
    from langgraph_api.encryption.aes_json import get_aes_encryption_instance
    from langgraph_api.encryption.custom import (
        JsonEncryptionWrapper,
        get_custom_encryption_instance,
    )

    custom_instance = get_custom_encryption_instance()
    aes = get_aes_encryption_instance()

    if custom_instance:
        # Wrap custom encryption with AES migration support (can decrypt old AES data)
        return JsonEncryptionWrapper(custom_instance, aes)
    return aes
