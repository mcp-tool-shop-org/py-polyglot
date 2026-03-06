"""Tests for the translate_all module (pure logic, no Ollama)."""

from pypolyglot.translate_all import (
    TRANSLATE_ALL_LANGUAGES,
    TargetLanguage,
    build_nav_bar,
    inject_nav_bar,
)


def test_translate_all_languages_count():
    assert len(TRANSLATE_ALL_LANGUAGES) == 7


def test_translate_all_languages_codes():
    codes = {l.code for l in TRANSLATE_ALL_LANGUAGES}
    assert "ja" in codes
    assert "zh" in codes
    assert "es" in codes
    assert "fr" in codes
    assert "hi" in codes
    assert "it" in codes
    assert "pt" in codes


def test_target_language_file_suffix():
    pt = next(l for l in TRANSLATE_ALL_LANGUAGES if l.code == "pt")
    assert pt.file == "pt-BR"
    ja = next(l for l in TRANSLATE_ALL_LANGUAGES if l.code == "ja")
    assert ja.file is None


def test_build_nav_bar():
    langs = TRANSLATE_ALL_LANGUAGES[:3]
    succeeded = {"ja", "zh", "es"}
    nav = build_nav_bar(langs, succeeded)
    assert '<p align="center">' in nav
    assert "README.ja.md" in nav
    assert "README.zh.md" in nav
    assert "README.es.md" in nav


def test_build_nav_bar_current_lang():
    langs = TRANSLATE_ALL_LANGUAGES[:2]
    succeeded = {"ja", "zh"}
    nav = build_nav_bar(langs, succeeded, current_lang_code="ja")
    assert "README.md" in nav  # Links to English for current lang
    assert "README.zh.md" in nav


def test_build_nav_bar_filters_failed():
    langs = TRANSLATE_ALL_LANGUAGES[:3]
    succeeded = {"ja"}  # Only ja succeeded
    nav = build_nav_bar(langs, succeeded)
    assert "README.ja.md" in nav
    assert "README.zh.md" not in nav


def test_inject_nav_bar_no_existing():
    md = "# Title\n\nContent here."
    nav = '<p align="center">\n  <a href="README.ja.md">JP</a>\n</p>'
    result = inject_nav_bar(md, nav)
    assert result.startswith('<p align="center">')
    assert "# Title" in result
    assert "Content here." in result


def test_inject_nav_bar_replaces_existing():
    md = (
        '<p align="center">\n'
        '  <a href="README.ja.md">JP</a>\n'
        '</p>\n\n'
        '# Title\n\nContent.'
    )
    new_nav = '<p align="center">\n  <a href="README.zh.md">ZH</a>\n</p>'
    result = inject_nav_bar(md, new_nav)
    assert "README.zh.md" in result
    assert result.count('<p align="center">') == 1  # Only the new one
