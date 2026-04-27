"""
Content safety guard — blocks racism, hate speech, and foul language
from entering the pipeline or appearing in generated scripts.

Two layers:
  1. Fast keyword pre-filter — catches obvious cases instantly
  2. Claude classifier — catches subtle and contextual violations
"""

import os
import re

import anthropic

# ── Layer 1: keyword blocklist ────────────────────────────────────────────────
# Kept deliberately short — Claude handles nuance; this stops obvious cases fast.
_BLOCKED_PATTERNS = [
    r"\bn[i*!1]+gg[ae]r\b",
    r"\bk[i*]+ke\b",
    r"\bsp[i*]+c\b",
    r"\bch[i*]+nk\b",
    r"\bwetback\b",
    r"\bcr[a*]+cker\b",
    r"\bf[a*4]+gg[o0]+t\b",
    r"\bdy[k*]+e\b",
    r"\br[e3]t[a@]rd\b",
    r"\bk[i*]ll\s+(all\s+)?(jews?|blacks?|muslims?|gays?|women)\b",
    r"\bheil\s+hitler\b",
    r"\bwhite\s+(power|supremac)",
    r"\bblack\s+lives\s+don.t\s+matter\b",
    r"\bgo\s+back\s+to\s+(your\s+)?(country|africa|mexico)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _BLOCKED_PATTERNS]


def _keyword_check(text: str) -> str | None:
    """Return a short reason string if a blocked pattern is found, else None."""
    for pattern in _COMPILED:
        if pattern.search(text):
            return "Content contains a prohibited slur or hate phrase."
    return None


# ── Layer 2: Claude classifier ────────────────────────────────────────────────
_SAFETY_PROMPT = """\
You are a content safety classifier. Your only job is to decide whether the text below contains:
- Racism or racial slurs
- Hate speech targeting any group (religion, gender, sexuality, ethnicity, nationality, disability)
- Calls for violence or discrimination
- Severe foul/abusive language clearly intended to harm or demean

Respond ONLY with one of these two formats — nothing else:
SAFE
BLOCKED: <one short sentence explaining what was found>

Text to evaluate:
---
{text}
---"""


def _claude_check(text: str) -> str | None:
    """Return a reason string if Claude flags the content, else None."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    # Cap at 3000 chars — enough for classification without burning tokens
    sample = text[:3000]
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",   # cheapest model, fast for classification
        max_tokens=60,
        temperature=0,
        messages=[{"role": "user", "content": _SAFETY_PROMPT.format(text=sample)}],
    )
    response = message.content[0].text.strip()
    if response.startswith("BLOCKED:"):
        return response[len("BLOCKED:"):].strip()
    return None


# ── Public API ────────────────────────────────────────────────────────────────

class ContentViolationError(ValueError):
    """Raised when input or generated content fails the safety check."""


def check(text: str, context: str = "input") -> None:
    """
    Run both safety layers against `text`.
    Raises ContentViolationError if either layer flags it.
    `context` is used in the error message ('input' or 'generated script').
    """
    reason = _keyword_check(text) or _claude_check(text)
    if reason:
        raise ContentViolationError(
            f"Content blocked in {context}: {reason}\n\n"
            "PodcastIQ does not process content that contains racism, hate speech, "
            "foul language, or discrimination of any kind."
        )
