"""
Output validation for translations.

Catches common failure modes: empty output, identical to source,
truncation, garbled text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .errors import ErrorCode, PolyglotError

MIN_LENGTH_RATIO = 0.15
MAX_LENGTH_RATIO = 8.0
LENGTH_CHECK_THRESHOLD = 20


@dataclass
class ValidationResult:
    valid: bool
    warnings: list[str] = field(default_factory=list)


_TECHNICAL_RE = re.compile(r"^[`~<>@#$*|\-\d\s.,:;/\\()\[\]{}]+$")
_BACKTICK_RE = re.compile(r"^`[^`]+`$")
_CONTROL_RE = re.compile(r"[\uFFFD\u0000-\u0008\u000E-\u001F]")
_META_PATTERNS = [
    re.compile(r"^(here(?:'s| is) (?:the|my|a) translation)", re.IGNORECASE),
    re.compile(r"^(translation:)", re.IGNORECASE),
    re.compile(r"^(note:|disclaimer:)", re.IGNORECASE),
]


def validate_translation(
    source: str,
    translation: str,
    source_lang: str,
    target_lang: str,
) -> ValidationResult:
    """Validate a translation result.

    Returns a ValidationResult with warnings. Throws PolyglotError for
    critical failures (empty output).
    """
    warnings: list[str] = []

    if not translation or not translation.strip():
        raise PolyglotError(
            code=ErrorCode.TRANSLATE_ERROR,
            message="Translation returned empty output.",
            hint="The model may be overloaded or the input may be too short to translate.",
            retryable=True,
        )

    src_trimmed = source.strip()
    tgt_trimmed = translation.strip()

    # Echo detection
    if src_trimmed == tgt_trimmed and source_lang != target_lang:
        is_technical = (
            bool(_TECHNICAL_RE.match(src_trimmed))
            or bool(_BACKTICK_RE.match(src_trimmed))
            or len(src_trimmed) <= 15
        )
        if not is_technical:
            warnings.append(
                f"Translation is identical to source text (possible echo). "
                f"Source lang: {source_lang}, target: {target_lang}."
            )

    # Length ratio checks
    if len(src_trimmed) >= LENGTH_CHECK_THRESHOLD:
        ratio = len(tgt_trimmed) / len(src_trimmed)

        if ratio < MIN_LENGTH_RATIO:
            warnings.append(
                f"Translation may be truncated: output is {ratio * 100:.0f}% of "
                f"source length (expected ≥{MIN_LENGTH_RATIO * 100:.0f}%)."
            )

        if ratio > MAX_LENGTH_RATIO:
            warnings.append(
                f"Translation may contain hallucinated text: output is {ratio * 100:.0f}% of "
                f"source length (expected ≤{MAX_LENGTH_RATIO * 100:.0f}%)."
            )

    # Garbled text detection
    control_chars = len(_CONTROL_RE.findall(tgt_trimmed))
    if control_chars > len(tgt_trimmed) * 0.05:
        warnings.append(
            f"Translation contains {control_chars} replacement/control characters "
            "— possible encoding issue."
        )

    # Meta-commentary detection
    for pat in _META_PATTERNS:
        match = pat.match(tgt_trimmed)
        if match:
            warnings.append(
                f'Translation may contain model commentary: "{match.group(1)}…". '
                "Consider stripping the prefix."
            )

    return ValidationResult(valid=len(warnings) == 0, warnings=warnings)


def is_valid_translation(
    source: str,
    translation: str,
    source_lang: str,
    target_lang: str,
) -> bool:
    """Quick boolean check for use in pipelines."""
    try:
        result = validate_translation(source, translation, source_lang, target_lang)
        return result.valid
    except PolyglotError:
        return False
