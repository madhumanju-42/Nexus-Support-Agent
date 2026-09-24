"""
Validation helper functions for input and output guardrails.

These functions apply the regex patterns from patterns.py and return
structured results that the guardrail nodes use to update state.
"""

from typing import Tuple, List
from guardrails.patterns import (
    PII_PATTERNS,
    PII_PLACEHOLDERS,
    INJECTION_PATTERNS,
    SCOPE_VIOLATION_PATTERNS,
)


def scan_and_redact_pii(text: str) -> Tuple[str, bool, List[str]]:
    """
    Scan text for PII and replace matches with placeholders.

    Returns:
        (redacted_text, pii_found, list_of_pii_types_found)
    """
    redacted = text
    found_types: List[str] = []

    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(redacted):
            found_types.append(pii_type)
            redacted = pattern.sub(PII_PLACEHOLDERS[pii_type], redacted)

    return redacted, len(found_types) > 0, found_types


def check_injection_regex(text: str) -> Tuple[bool, str]:
    """
    Check text against known injection patterns.

    Returns:
        (is_injection, matched_pattern_snippet)
    """
    for pattern in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            return True, match.group(0)
    return False, ""


def check_scope_violations(text: str) -> List[str]:
    """
    Check agent output for unauthorized action claims.

    Returns:
        List of violation descriptions found.
    """
    violations: List[str] = []
    for pattern in SCOPE_VIOLATION_PATTERNS:
        match = pattern.search(text)
        if match:
            violations.append(f"scope_violation: '{match.group(0)}'")
    return violations


def check_output_pii(text: str) -> List[str]:
    """
    Check agent output for PII leaks (same patterns as input).

    Returns:
        List of PII types leaked in the output.
    """
    leaked: List[str] = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            leaked.append(f"pii_leak: {pii_type}")
    return leaked
