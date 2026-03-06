"""
MCP server — Local GPU translation via TranslateGemma + Ollama.
Zero cloud dependency, 57 languages, runs on your GPU.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .errors import friendly_error
from .glossary import GlossaryEntry
from .languages import LANGUAGES
from .ollama import OllamaClient
from .translate import TranslateOptions, translate
from .markdown import TranslateMarkdownOptions, translate_markdown
from .translate_all import TRANSLATE_ALL_LANGUAGES, translate_all

mcp = FastMCP(name="py-polyglot")


@mcp.tool()
async def translate_text(
    text: str,
    from_lang: str,
    to_lang: str,
    model: str | None = None,
    glossary: dict[str, str] | None = None,
) -> str:
    """Translate text between any of 57 supported languages using TranslateGemma
    running locally on your GPU via Ollama. Automatically starts Ollama and pulls
    the model if needed. Includes a built-in software glossary.

    Args:
        text: The text to translate
        from_lang: Source language code or name (e.g., "en", "English")
        to_lang: Target language code or name (e.g., "es", "Spanish")
        model: Ollama model (default: "translategemma:12b")
        glossary: Custom term overrides as {"source term": "target translation"}
    """
    try:
        custom_glossary = None
        if glossary:
            custom_glossary = [
                GlossaryEntry(
                    term=term,
                    translations={to_lang.split("-")[0].lower(): translation},
                )
                for term, translation in glossary.items()
            ]

        opts = TranslateOptions(model=model, glossary=custom_glossary)
        result = await translate(text, from_lang, to_lang, opts)
        secs = result.duration_ms / 1000
        parts = [result.translation]
        parts.append(
            f"\n---\n{result.source_language.name} -> {result.target_language.name} | "
            f"{result.model} | {result.chunks} chunk(s) | {secs:.1f}s"
        )
        if result.warnings:
            parts.append("\nWarnings:\n" + "\n".join(f"  - {w}" for w in result.warnings))
        return "\n".join(parts)
    except Exception as err:
        return friendly_error(err)


@mcp.tool()
async def list_languages() -> str:
    """List all 57 languages supported by TranslateGemma for translation."""
    lines = [f"{lang.code:<8} {lang.name}" for lang in LANGUAGES]
    return f"Supported languages ({len(LANGUAGES)}):\n\n" + "\n".join(lines)


@mcp.tool()
async def translate_md(
    markdown: str,
    from_lang: str,
    to_lang: str,
    model: str | None = None,
) -> str:
    """Translate a markdown document while preserving its structure.
    Code blocks, HTML elements, URLs, badges, and table formatting are kept intact.

    Args:
        markdown: The full markdown content to translate
        from_lang: Source language code or name (e.g., "en", "English")
        to_lang: Target language code or name (e.g., "ja", "Japanese")
        model: Ollama model (default: "translategemma:12b")
    """
    try:
        opts = TranslateMarkdownOptions(model=model, cache=False)
        result = await translate_markdown(markdown, from_lang, to_lang, opts)
        secs = result.duration_ms / 1000
        parts = [result.markdown]
        parts.append(
            f"\n---\n{result.segments} segments | {result.translated} translated | "
            f"{result.cached} cached | {result.fuzzy_matched} fuzzy | "
            f"{result.ollama_calls} Ollama call(s) | {secs:.1f}s"
        )
        if result.warnings:
            parts.append("\nWarnings:\n" + "\n".join(f"  - {w}" for w in result.warnings))
        return "\n".join(parts)
    except Exception as err:
        return friendly_error(err)


@mcp.tool()
async def translate_all_langs(
    markdown: str,
    from_lang: str = "en",
    languages: list[str] | None = None,
    model: str | None = None,
    concurrency: int = 2,
    nav_bar: bool = True,
) -> str:
    """Translate markdown content into multiple languages at once
    (default: 7 languages). Runs translations concurrently.

    Args:
        markdown: The full markdown content to translate
        from_lang: Source language code (default: "en")
        languages: Target language codes (default: all 7)
        model: Ollama model (default: "translategemma:12b")
        concurrency: Max concurrent language translations (default: 2, max: 3)
        nav_bar: Inject a language nav bar at the top (default: true)
    """
    try:
        result = await translate_all(
            markdown,
            source_lang=from_lang,
            target_langs=languages,
            model=model,
            concurrency=concurrency,
            nav_bar=nav_bar,
        )

        secs = result.duration_ms / 1000
        parts: list[str] = []
        for r in result.results:
            if r.status == "ok" and r.markdown:
                parts.append(f"--- README.{r.file_suffix}.md ---\n{r.markdown}")
            else:
                parts.append(f"--- README.{r.file_suffix}.md --- ERROR: {r.error}")

        parts.append(f"\n---\n{result.succeeded} succeeded | {result.failed} failed | {secs:.1f}s total")
        return "\n".join(parts)
    except Exception as err:
        return friendly_error(err)


@mcp.tool()
async def check_status() -> str:
    """Check if Ollama is running and TranslateGemma models are available."""
    client = OllamaClient()

    available = await client.ensure_running()
    if not available:
        return "\n".join([
            "Ollama is not installed or could not be started.",
            "",
            "To fix this:",
            "  1. Install Ollama from https://ollama.com",
            "  2. Run: ollama serve",
            "  3. Try again",
        ])

    models = await client.list_models()
    tg_models = [m for m in models if m.name.startswith("translategemma")]

    if not tg_models:
        return "\n".join([
            "Ollama is running but no TranslateGemma model is installed.",
            "",
            "Pick a model based on your GPU:",
            "  ollama pull translategemma:4b    3.3 GB  (fast, good quality)",
            "  ollama pull translategemma:12b   8.1 GB  (balanced -- recommended)",
            "  ollama pull translategemma:27b   17 GB   (slow, best quality)",
            "",
            "Note: The translate tool will auto-pull the model on first use.",
        ])

    model_list = "\n".join(f"  {m.name} ({m.size / 1e9:.1f} GB)" for m in tg_models)
    return f"Ready to translate. TranslateGemma models installed:\n{model_list}"
