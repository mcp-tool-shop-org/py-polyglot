"""
Structured error handling for Polyglot.

Follows the Shipcheck Tier 1 error contract:
  code · message · hint · cause? · retryable?
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    OLLAMA_UNAVAILABLE = "OLLAMA_UNAVAILABLE"
    OLLAMA_TIMEOUT = "OLLAMA_TIMEOUT"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    MODEL_PULL_FAILED = "MODEL_PULL_FAILED"
    UNSUPPORTED_LANGUAGE = "UNSUPPORTED_LANGUAGE"
    SAME_LANGUAGE = "SAME_LANGUAGE"
    NETWORK_ERROR = "NETWORK_ERROR"
    OLLAMA_ERROR = "OLLAMA_ERROR"
    TRANSLATE_ERROR = "TRANSLATE_ERROR"


class PolyglotError(Exception):
    """Structured error with code, message, hint, and retryable flag."""

    def __init__(
        self,
        *,
        code: ErrorCode,
        message: str,
        hint: Optional[str] = None,
        cause: Optional[Exception] = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.code = code
        self.hint = hint
        self.retryable = retryable
        self.__cause__ = cause

    def to_user_string(self) -> str:
        parts = [str(self)]
        if self.hint:
            parts.append(self.hint)
        return "\n".join(parts)

    def to_mcp_result(self) -> dict:
        result: dict = {
            "code": self.code.value,
            "message": str(self),
            "retryable": self.retryable,
        }
        if self.hint:
            result["hint"] = self.hint
        return result


def friendly_error(err: BaseException) -> str:
    """Convert any thrown value to a user-friendly error string."""
    if isinstance(err, PolyglotError):
        return err.to_user_string()

    msg = str(err)

    if "Cannot connect" in msg or "connect" in msg.lower():
        return "\n".join([
            "Cannot reach Ollama.",
            "",
            "Polyglot tried to auto-start it but couldn't connect.",
            "Make sure Ollama is installed (https://ollama.com) and try again.",
        ])

    if "not found" in msg:
        return "\n".join([
            msg,
            "",
            "The translate tool normally auto-pulls models, but the pull may have",
            "failed. Check your internet connection and try: ollama pull translategemma:12b",
        ])

    if "Unsupported" in msg:
        return "\n".join([
            msg,
            "",
            "Use the list_languages tool to see all 57 supported languages.",
            'You can use either language codes ("en") or names ("English").',
        ])

    if "must be different" in msg:
        return "Source and target languages are the same — nothing to translate."

    return f"Translation failed: {msg}"
