# cx-kit/src/cx_kit/utils/serialization.py

"""
Provides low-level, pure-Python data serialization utilities.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID


def safe_serialize(data: Any) -> Any:
    """
    Recursively traverses a data structure and converts common, non-standard
    JSON types (like datetime, UUID, Decimal) into a JSON-serializable format.

    This utility is essential for ensuring that data can be reliably passed
    between components, written to manifests, or sent over the network.
    """

    if isinstance(data, list):
        return [safe_serialize(item) for item in data]

    if isinstance(data, dict):
        return {key: safe_serialize(value) for key, value in data.items()}

    # Handle datetime objects first, as they are a subclass of date.
    if isinstance(data, datetime):
        if data.tzinfo is None:
            # If the datetime is naive, assume it's UTC for consistency.
            data = data.replace(tzinfo=timezone.utc)
        # Use the standard 'Z' suffix for UTC.
        return data.isoformat().replace("+00:00", "Z")

    # Now handle date objects, which do not have tzinfo.
    if isinstance(data, date):
        return data.isoformat()

    if isinstance(data, UUID):
        return str(data)

    if isinstance(data, Decimal):
        return float(data)

    # Safely handle special objects with a string-like `id` attribute
    # which are common in some database clients.
    if (
        hasattr(data, "id")
        and isinstance(getattr(data, "id", None), str)
        and ":" in data.id
    ):
        return str(data)

    # For all other types, return as is. The `json.dumps` default handler
    # will raise a TypeError if it's not serializable.
    return data
