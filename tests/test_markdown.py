"""Tests for markdown module."""

from pypolyglot.markdown import (
    segment_markdown,
    is_translatable_cell,
    parse_table,
    extract_tagline_text,
    rebuild_tagline,
    clean_translation,
)


def test_segment_code_block():
    md = "text\n```python\ncode\n```\nmore"
    segments = segment_markdown(md)
    types = [s.type for s in segments]
    assert "protected" in types


def test_segment_heading():
    md = "## Hello World"
    segments = segment_markdown(md)
    heading = [s for s in segments if s.type == "heading"][0]
    assert heading.prefix == "## "
    assert heading.text == "Hello World"


def test_segment_paragraph():
    md = "This is a paragraph.\nWith two lines."
    segments = segment_markdown(md)
    assert any(s.type == "text" for s in segments)


def test_segment_table():
    md = "| A | B |\n|---|---|\n| x | y |"
    segments = segment_markdown(md)
    assert any(s.type == "table" for s in segments)


def test_segment_html_block():
    md = '<div align="center">\n<img src="logo.png">\n</div>'
    segments = segment_markdown(md)
    assert segments[0].type == "protected"


def test_segment_empty_line():
    md = "text\n\nmore"
    segments = segment_markdown(md)
    assert any(s.type == "protected" and s.text == "" for s in segments)


def test_is_translatable_cell_prose():
    assert is_translatable_cell("Local GPU translation") is True


def test_is_translatable_cell_backtick():
    assert is_translatable_cell("`code`") is False


def test_is_translatable_cell_number():
    assert is_translatable_cell("3.14") is False


def test_is_translatable_cell_link():
    assert is_translatable_cell("[text](url)") is False


def test_is_translatable_cell_short():
    assert is_translatable_cell("ab") is False


def test_parse_table():
    table = "| A | Description |\n|---|---|\n| `x` | Some text |"
    parsed, cells = parse_table(table)
    assert len(parsed) == 3
    assert len(cells) >= 1


def test_extract_tagline_text():
    line = '<p align="center"><strong>Hello World</strong></p>'
    assert extract_tagline_text(line) == "Hello World"


def test_extract_tagline_no_match():
    assert extract_tagline_text("<p>No strong tag</p>") is None


def test_rebuild_tagline():
    original = '<p align="center"><strong>Hello</strong></p>'
    result = rebuild_tagline(original, "こんにちは")
    assert "こんにちは" in result
    assert "<strong>" in result


def test_clean_translation_or_pattern():
    text = "翻訳A\nまたは\n翻訳B"
    assert clean_translation(text) == "翻訳A"


def test_clean_translation_heading():
    assert clean_translation("タイトル。", is_heading=True) == "タイトル"
