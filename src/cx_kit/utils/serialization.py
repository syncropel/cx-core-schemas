# cx-kit/src/cx_kit/utils/serialization.py

"""
Provides a robust, production-grade, and forward-facing data serialization utility.

This module is the single source of truth for converting complex Python objects
from various data science libraries (Pandas, NumPy) and standard libraries
into a format that is 100% compatible with JSON.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID
from pydantic import BaseModel

# --- Lazy, Safe Imports for Optional Heavy Dependencies ---
# We use a try/except block to avoid a hard dependency on numpy and pandas.
# The serialization logic will only apply if these libraries are installed
# in the environment where this function is called.
try:
    import numpy as np

    _NUMPY_AVAILABLE = True
except ImportError:
    np = None
    _NUMPY_AVAILABLE = False

try:
    import pandas as pd

    _PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    _PANDAS_AVAILABLE = False


def safe_serialize(data: Any) -> Any:
    """
    Recursively traverses a data structure and converts common, non-standard
    JSON types (like datetime, UUID, Decimal, and types from NumPy/Pandas)
    into a JSON-serializable format.

    This is the definitive serialization function for the Syncropel platform.

    Args:
        data: The Python object or data structure to serialize.

    Returns:
        A new data structure containing only JSON-compatible types
        (lists, dicts, strings, numbers, booleans, None).
    """

    # --- Structural Types (Recursive) ---
    if isinstance(data, list):
        return [safe_serialize(item) for item in data]

    if isinstance(data, dict):
        return {str(key): safe_serialize(value) for key, value in data.items()}

    # --- Pydantic Models ---
    if isinstance(data, BaseModel):
        # Recursively serialize the model's dictionary representation.
        return safe_serialize(data.model_dump())

    # --- Datetime and Timedelta Types ---
    if _PANDAS_AVAILABLE and isinstance(data, pd.Timestamp):
        # Convert Pandas Timestamp to a standard Python datetime object.
        data = data.to_pydatetime()

    if isinstance(data, datetime):
        # Ensure timezone-awareness for consistency (assume UTC if naive).
        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)
        # Use the standard ISO 8601 format with 'Z' for UTC.
        return data.isoformat().replace("+00:00", "Z")

    if isinstance(data, date):
        return data.isoformat()

    # --- NumPy Specific Types (if available) ---
    if _NUMPY_AVAILABLE:
        # For scalar types like np.int64, np.float64, np.bool_
        if isinstance(data, np.generic):
            return data.item()
        # For NumPy arrays
        if isinstance(data, np.ndarray):
            return data.tolist()

    # --- Other Standard Library Types ---
    if isinstance(data, UUID):
        return str(data)

    if isinstance(data, Decimal):
        return float(data)

    # --- Special Case for `bytes` ---
    if isinstance(data, bytes):
        # Attempt to decode as UTF-8, with a fallback for non-text data.
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return f"<binary data of size {len(data)} bytes>"

    # For all other types, return as is. The `json.dumps` default handler
    # will raise a TypeError if it's not a known JSON type.
    return data
