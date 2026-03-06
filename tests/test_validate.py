"""Tests for validate module."""

import pytest

from pypolyglot.errors import PolyglotError
from pypolyglot.validate import validate_translation, is_valid_translation


def test_valid_translation():
    result = validate_translation("Hello world", "こんにちは世界", "en", "ja")
    assert result.valid
    assert result.warnings == []


def test_empty_translation_raises():
    with pytest.raises(PolyglotError):
        validate_translation("Hello", "", "en", "ja")


def test_echo_detection():
    result = validate_translation(
        "This is a long enough sentence to test",
        "This is a long enough sentence to test",
        "en", "ja"
    )
    assert not result.valid
    assert any("identical" in w for w in result.warnings)


def test_echo_skips_short_text():
    result = validate_translation("x = 1", "x = 1", "en", "ja")
    assert result.valid  # Short technical text


def test_truncation_warning():
    source = "A" * 100
    translation = "B" * 5  # 5% of source
    result = validate_translation(source, translation, "en", "ja")
    assert any("truncated" in w for w in result.warnings)


def test_hallucination_warning():
    source = "A" * 100
    translation = "B" * 900  # 900% of source
    result = validate_translation(source, translation, "en", "ja")
    assert any("hallucinated" in w for w in result.warnings)


def test_meta_commentary_detection():
    result = validate_translation(
        "Hello world",
        "Here is the translation: こんにちは世界",
        "en", "ja"
    )
    assert any("commentary" in w for w in result.warnings)


def test_is_valid_translation_convenience():
    assert is_valid_translation("Hello", "こんにちは", "en", "ja") is True
    assert is_valid_translation("Hello", "", "en", "ja") is False
