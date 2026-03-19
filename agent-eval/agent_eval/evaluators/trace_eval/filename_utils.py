"""
Shared filename sanitization utilities.

This module provides filename sanitization used by runner, reporting,
and pipeline layers. Centralizing here avoids duplication and prevents
inverted dependency directions (e.g., runner importing from reporting).

Design decisions:
- Multiple unsafe chars produce multiple underscores (no collapsing).
  This preserves positional information and matches existing test expectations.
- Truncation happens after first strip, then a second strip cleans up
  any trailing dots/underscores exposed by truncation.
- Windows reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9) are
  prefixed with an underscore for cross-platform safety.
- Non-string input is coerced to str for defensive robustness.
  Callers passing None get "run" fallback rather than a TypeError.
- No extension-aware truncation: this utility is for run IDs and
  identifiers, not user-facing filenames with meaningful extensions.
"""

import re

# Windows reserved device names (case-insensitive).
# These cannot be used as filenames on Windows, even with extensions.
_WINDOWS_RESERVED = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
})


def sanitize_filename(text: str, max_length: int = 100) -> str:
    """
    Sanitize text for use in filenames.

    Replaces non-alphanumeric characters (except . _ -) with underscores,
    strips leading/trailing dots and underscores, truncates to max_length,
    and handles Windows reserved names.
    Returns "run" as fallback if result is empty or None.

    Args:
        text: Text to sanitize. Non-string values are coerced via str().
        max_length: Maximum length of sanitized text (must be >= 1)

    Returns:
        Sanitized text safe for use in filenames (never empty)

    Examples:
        >>> sanitize_filename("test_run_001")
        'test_run_001'
        >>> sanitize_filename("test/run/../001")
        'test_run___001'
        >>> sanitize_filename("...test___")
        'test'
        >>> sanitize_filename("")
        'run'
        >>> sanitize_filename("CON")
        '_CON'
        >>> sanitize_filename(None)
        'run'
    """
    if max_length < 1:
        return "run"

    # Defensive coercion: handle None and non-string callers gracefully
    if text is None:
        return "run"
    if not isinstance(text, str):
        text = str(text)

    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', text)
    sanitized = sanitized.strip('._')
    sanitized = sanitized[:max_length].strip('._')

    if not sanitized:
        return "run"

    # Guard against Windows reserved device names
    if sanitized.upper() in _WINDOWS_RESERVED:
        sanitized = f"_{sanitized}"
        # Re-truncate if prefix pushed past max_length
        sanitized = sanitized[:max_length]

    return sanitized
