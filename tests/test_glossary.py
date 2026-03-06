"""Tests for glossary module."""

from pypolyglot.glossary import SOFTWARE_GLOSSARY, GlossaryEntry, build_glossary_hint


def test_software_glossary_has_entries():
    assert len(SOFTWARE_GLOSSARY) == 12


def test_build_glossary_hint_matching():
    hint = build_glossary_hint("Deploy the Library", "ja", SOFTWARE_GLOSSARY)
    assert '"Deploy"' in hint
    assert '"Library"' in hint
    assert "デプロイ" in hint
    assert "ライブラリ" in hint


def test_build_glossary_hint_no_match():
    hint = build_glossary_hint("Hello world", "ja", SOFTWARE_GLOSSARY)
    assert hint == ""


def test_build_glossary_hint_no_translation_for_lang():
    hint = build_glossary_hint("Deploy the Library", "sw", SOFTWARE_GLOSSARY)
    # Swahili has no deploy/library translations in the glossary
    assert hint == ""


def test_custom_glossary():
    custom = [GlossaryEntry("Widget", {"ja": "ウィジェット"})]
    hint = build_glossary_hint("Widget factory", "ja", custom)
    assert '"Widget"' in hint
    assert "ウィジェット" in hint
