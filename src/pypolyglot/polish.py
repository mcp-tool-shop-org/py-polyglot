"""
Post-translation polish layer.

Cleans up common TranslateGemma output quirks so the result
reads naturally without manual fixup.
"""

from __future__ import annotations

import re

# Patterns where TranslateGemma outputs alternative translations
# separated by "or" in the target language.
_OR_PATTERNS = [
    re.compile(r"\nまたは\n.*", re.DOTALL),       # Japanese
    re.compile(r"\n또는\n.*", re.DOTALL),         # Korean
    re.compile(r"\no\n(?=[A-Z]).*", re.DOTALL),   # Spanish/Italian/Portuguese
    re.compile(r"\nou\n.*", re.DOTALL),            # French/Portuguese
    re.compile(r"\noder\n.*", re.DOTALL),          # German
    re.compile(r"\nили\n.*", re.DOTALL),           # Russian
    re.compile(r"\nया\n.*", re.DOTALL),            # Hindi
    re.compile(r"\nveya\n.*", re.DOTALL),          # Turkish
    re.compile(r"\nหรือ\n.*", re.DOTALL),          # Thai
    re.compile(r"\nhoặc\n.*", re.DOTALL),          # Vietnamese
    re.compile(r"\natau\n.*", re.DOTALL),          # Indonesian/Malay
    re.compile(r"\nof\n(?=[A-Z]).*", re.DOTALL),   # Afrikaans
]

_TRAILING_PERIOD = re.compile(r"[。．.。]\s*$")
_TRAILING_SPACES = re.compile(r"[ \t]+\n")
_TRIPLE_NEWLINES = re.compile(r"\n{3,}")
_LINE_EDGE_SPACES = re.compile(r"^[ \t]+|[ \t]+$", re.MULTILINE)


def polish(text: str) -> str:
    """Clean up a translated string."""
    result = text

    for pat in _OR_PATTERNS:
        result = pat.sub("", result)

    result = _TRAILING_SPACES.sub("\n", result)
    result = _TRIPLE_NEWLINES.sub("\n\n", result)
    result = _LINE_EDGE_SPACES.sub("", result)

    return result.strip()


def polish_heading(text: str) -> str:
    """Polish with heading-specific rules (strip trailing periods)."""
    result = polish(text)
    result = _TRAILING_PERIOD.sub("", result)
    return result


def polish_cell(text: str) -> str:
    """Polish a table cell — strip alternatives and trailing periods,
    but preserve the cell's inline formatting."""
    result = polish(text)
    result = result.replace("\n", " ")
    return result
