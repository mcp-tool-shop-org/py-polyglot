"""
py-polyglot — Local GPU translation via TranslateGemma + Ollama.

57 languages, zero cloud dependency. Use as a Python library or MCP server.

Library usage:
    from pypolyglot import translate, translate_markdown, translate_all
    from pypolyglot import list_languages, check_status

    result = await translate("Hello world", "en", "ja")

MCP server:
    python -m pypolyglot
    # or
    py-polyglot
"""

__version__ = "1.0.1"

from .translate import translate, translate_batch, TranslateResult, TranslateOptions
from .markdown import translate_markdown, TranslateMarkdownResult, TranslateMarkdownOptions
from .translate_all import translate_all, TranslateAllResult, TRANSLATE_ALL_LANGUAGES
from .languages import LANGUAGES, Language, resolve_language, is_supported
from .ollama import OllamaClient
from .cache import TranslationCache, load_cache, save_cache, create_cache
from .errors import PolyglotError, ErrorCode, friendly_error
from .glossary import GlossaryEntry, SOFTWARE_GLOSSARY, build_glossary_hint

__all__ = [
    # Core
    "translate",
    "translate_batch",
    "translate_markdown",
    "translate_all",
    # Results
    "TranslateResult",
    "TranslateMarkdownResult",
    "TranslateAllResult",
    # Options
    "TranslateOptions",
    "TranslateMarkdownOptions",
    # Languages
    "LANGUAGES",
    "Language",
    "resolve_language",
    "is_supported",
    "TRANSLATE_ALL_LANGUAGES",
    # Ollama
    "OllamaClient",
    # Cache
    "TranslationCache",
    "load_cache",
    "save_cache",
    "create_cache",
    # Errors
    "PolyglotError",
    "ErrorCode",
    "friendly_error",
    # Glossary
    "GlossaryEntry",
    "SOFTWARE_GLOSSARY",
    "build_glossary_hint",
]
