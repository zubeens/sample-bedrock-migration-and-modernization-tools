"""
Shared JSON utilities for the trace-eval subsystem.

Centralised here so that both pipeline and runner can use them
without creating inverted dependency directions.
"""

import json
from datetime import datetime
from decimal import Decimal


class SafeJSONEncoder(json.JSONEncoder):
    """
    JSON encoder that handles non-native JSON types safely.

    Converts:
    - datetime objects to ISO format strings
    - Decimal to float
    - Objects with __dict__ to their dict representation
    - Other non-serializable objects to string representation
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)


def validation_error_message(exc: Exception) -> str:
    """Extract a human-readable message from a validation exception.

    Works with ``ValidationError`` (which carries a ``.message`` attribute)
    and any other exception type (falls back to ``str(exc)``).
    """
    return exc.message if hasattr(exc, "message") else str(exc)
