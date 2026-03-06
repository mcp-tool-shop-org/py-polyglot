"""Tests for polish module."""

from pypolyglot.polish import polish, polish_heading, polish_cell


def test_polish_strips_japanese_or():
    text = "翻訳A\nまたは\n翻訳B"
    assert polish(text) == "翻訳A"


def test_polish_strips_korean_or():
    text = "번역A\n또는\n번역B"
    assert polish(text) == "번역A"


def test_polish_normalizes_whitespace():
    text = "line1   \n\n\n\nline2"
    result = polish(text)
    assert "   \n" not in result
    assert "\n\n\n" not in result


def test_polish_heading_strips_trailing_period():
    assert polish_heading("タイトル。") == "タイトル"
    assert polish_heading("Title.") == "Title"


def test_polish_cell_removes_newlines():
    assert "\n" not in polish_cell("cell\ntext")


def test_polish_preserves_content():
    text = "Simple text"
    assert polish(text) == "Simple text"
