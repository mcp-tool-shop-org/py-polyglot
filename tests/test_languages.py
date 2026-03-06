"""Tests for languages module."""

from pypolyglot.languages import LANGUAGES, resolve_language, is_supported


def test_language_count():
    assert len(LANGUAGES) == 57


def test_resolve_by_code():
    lang = resolve_language("en")
    assert lang is not None
    assert lang.code == "en"
    assert lang.name == "English"


def test_resolve_by_name():
    lang = resolve_language("Japanese")
    assert lang is not None
    assert lang.code == "ja"


def test_resolve_case_insensitive():
    assert resolve_language("EN") is not None
    assert resolve_language("english") is not None
    assert resolve_language("JAPANESE") is not None


def test_resolve_underscore_to_dash():
    lang = resolve_language("zh_Hant")
    assert lang is not None
    assert lang.code == "zh-Hant"


def test_resolve_unknown():
    assert resolve_language("xx") is None
    assert resolve_language("Klingon") is None


def test_is_supported():
    assert is_supported("en") is True
    assert is_supported("ja") is True
    assert is_supported("xx") is False
