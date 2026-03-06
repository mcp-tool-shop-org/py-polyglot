"""Tests for the errors module."""

from pypolyglot.errors import ErrorCode, PolyglotError, friendly_error


def test_error_code_values():
    assert ErrorCode.OLLAMA_UNAVAILABLE == "OLLAMA_UNAVAILABLE"
    assert ErrorCode.UNSUPPORTED_LANGUAGE == "UNSUPPORTED_LANGUAGE"


def test_polyglot_error_basic():
    err = PolyglotError(
        code=ErrorCode.OLLAMA_TIMEOUT,
        message="Timed out",
        hint="Try again",
        retryable=True,
    )
    assert str(err) == "Timed out"
    assert err.code == ErrorCode.OLLAMA_TIMEOUT
    assert err.hint == "Try again"
    assert err.retryable is True


def test_polyglot_error_to_user_string():
    err = PolyglotError(code=ErrorCode.NETWORK_ERROR, message="Failed", hint="Check network")
    assert "Failed" in err.to_user_string()
    assert "Check network" in err.to_user_string()


def test_polyglot_error_to_user_string_no_hint():
    err = PolyglotError(code=ErrorCode.NETWORK_ERROR, message="Failed")
    assert err.to_user_string() == "Failed"


def test_polyglot_error_to_mcp_result():
    err = PolyglotError(
        code=ErrorCode.MODEL_NOT_FOUND,
        message="Not found",
        hint="Pull it",
        retryable=False,
    )
    result = err.to_mcp_result()
    assert result["code"] == "MODEL_NOT_FOUND"
    assert result["message"] == "Not found"
    assert result["hint"] == "Pull it"
    assert result["retryable"] is False


def test_polyglot_error_to_mcp_result_no_hint():
    err = PolyglotError(code=ErrorCode.OLLAMA_ERROR, message="Error")
    result = err.to_mcp_result()
    assert "hint" not in result


def test_polyglot_error_cause():
    cause = ValueError("root cause")
    err = PolyglotError(code=ErrorCode.NETWORK_ERROR, message="Wrapped", cause=cause)
    assert err.__cause__ is cause


def test_friendly_error_polyglot_error():
    err = PolyglotError(code=ErrorCode.OLLAMA_TIMEOUT, message="Timeout", hint="Retry")
    result = friendly_error(err)
    assert "Timeout" in result
    assert "Retry" in result


def test_friendly_error_connection():
    result = friendly_error(RuntimeError("Cannot connect to Ollama"))
    assert "Ollama" in result


def test_friendly_error_not_found():
    result = friendly_error(RuntimeError("Model not found"))
    assert "not found" in result


def test_friendly_error_unsupported():
    result = friendly_error(RuntimeError("Unsupported language"))
    assert "list_languages" in result


def test_friendly_error_same_language():
    result = friendly_error(RuntimeError("must be different"))
    assert "same" in result


def test_friendly_error_generic():
    result = friendly_error(RuntimeError("Something weird"))
    assert "Translation failed" in result
