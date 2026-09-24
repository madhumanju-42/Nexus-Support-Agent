"""
Regex patterns for PII detection and prompt injection detection.

Used by both input and output guardrail nodes. Keeping patterns centralized
avoids duplication and makes them easy to update.
"""

import re

# ── PII Detection ─────────────────────────────────────────────────
# Each key is a PII type; the value is a compiled regex.

PII_PATTERNS = {
    "email": re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ),
    "ssn": re.compile(
        r'\b\d{3}-\d{2}-\d{4}\b'
    ),
    "credit_card": re.compile(
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    ),
    "phone": re.compile(
        r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    ),
}

# Placeholder text used when redacting each PII type
PII_PLACEHOLDERS = {
    "email": "[EMAIL_REDACTED]",
    "ssn": "[SSN_REDACTED]",
    "credit_card": "[CREDIT_CARD_REDACTED]",
    "phone": "[PHONE_REDACTED]",
}

# ── Prompt Injection Detection ────────────────────────────────────
# Each pattern targets a known injection technique.

INJECTION_PATTERNS = [
    re.compile(r'(?i)ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)'),
    re.compile(r'(?i)you\s+are\s+now\s+(a|an|the)'),
    re.compile(r'(?i)system\s*:\s*'),
    re.compile(r'(?i)pretend\s+(you\s+are|to\s+be)'),
    re.compile(r'(?i)disregard\s+(your|all|the)'),
    re.compile(r'(?i)forget\s+(everything|all|your)'),
    re.compile(r'(?i)new\s+instructions?\s*:'),
    re.compile(r'(?i)override\s+(your|the|all)'),
    re.compile(r'(?i)jailbreak'),
    re.compile(r'(?i)DAN\s+mode'),
]

# ── Output Scope Violations ───────────────────────────────────────
# Phrases that indicate the agent is promising actions it cannot perform.

SCOPE_VIOLATION_PATTERNS = [
    re.compile(r"(?i)i'?ve\s+(processed|completed|issued)\s+(your|the|a)\s+refund"),
    re.compile(r"(?i)i'?ve\s+updated\s+your\s+account"),
    re.compile(r"(?i)your\s+password\s+is"),
    re.compile(r"(?i)i'?ve\s+(cancelled|deleted|removed)\s+your"),
    re.compile(r"(?i)i'?ve\s+charged\s+your"),
]
