"""Tests for the translate module (pure logic, no Ollama)."""

from pypolyglot.translate import (
    build_prompt,
    build_batch_prompt,
    chunk_text,
    get_chunk_size,
    BATCH_SEPARATOR,
)
from pypolyglot.languages import resolve_language


def test_get_chunk_size_4b():
    assert get_chunk_size("translategemma:4b") == 2000
    assert get_chunk_size("translategemma:2b") == 2000


def test_get_chunk_size_12b():
    assert get_chunk_size("translategemma:12b") == 4000


def test_get_chunk_size_27b():
    assert get_chunk_size("translategemma:27b") == 6000


def test_get_chunk_size_default():
    assert get_chunk_size("some-other-model") == 4000


def test_chunk_text_short():
    result = chunk_text("Hello world", 100)
    assert result == ["Hello world"]


def test_chunk_text_paragraph_boundary():
    text = "Paragraph one.\n\nParagraph two."
    result = chunk_text(text, 20)
    assert len(result) == 2
    assert "one" in result[0]
    assert "two" in result[1]


def test_chunk_text_sentence_boundary():
    text = "First sentence. Second sentence. Third sentence."
    result = chunk_text(text, 30)
    assert len(result) >= 2


def test_chunk_text_no_good_boundary():
    text = "A" * 200
    result = chunk_text(text, 100)
    assert len(result) == 2
    assert len(result[0]) == 100


def test_build_prompt():
    source = resolve_language("en")
    target = resolve_language("ja")
    result = build_prompt(source, target, "Hello", "")
    assert "English" in result
    assert "Japanese" in result
    assert "Hello" in result


def test_build_prompt_with_glossary():
    source = resolve_language("en")
    target = resolve_language("ja")
    result = build_prompt(source, target, "Hello", " Glossary: Widget = ウィジェット")
    assert "Glossary" in result
    assert "ウィジェット" in result


def test_build_batch_prompt():
    source = resolve_language("en")
    target = resolve_language("fr")
    joined = f"Hello{BATCH_SEPARATOR}World"
    result = build_batch_prompt(source, target, joined, "")
    assert "POLYGLOT_SEP" in result
    assert "Hello" in result
    assert "World" in result


def test_batch_separator_preserved():
    """Batch separator should be a recognizable delimiter."""
    assert "POLYGLOT_SEP" in BATCH_SEPARATOR
    assert "\n" in BATCH_SEPARATOR
