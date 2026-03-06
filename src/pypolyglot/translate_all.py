"""
Multi-language translation orchestrator.

Translates markdown content into multiple languages concurrently,
with optional language nav bar injection.
"""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from .markdown import TranslateMarkdownOptions, translate_markdown
from .semaphore import Semaphore


@dataclass
class TargetLanguage:
    code: str
    name: str
    label: str
    file: Optional[str] = None


TRANSLATE_ALL_LANGUAGES: list[TargetLanguage] = [
    TargetLanguage("ja", "Japanese", "日本語"),
    TargetLanguage("zh", "Chinese (Simplified)", "中文"),
    TargetLanguage("es", "Spanish", "Español"),
    TargetLanguage("fr", "French", "Français"),
    TargetLanguage("hi", "Hindi", "हिन्दी"),
    TargetLanguage("it", "Italian", "Italiano"),
    TargetLanguage("pt", "Portuguese", "Português (BR)", file="pt-BR"),
]


@dataclass
class TranslateAllLanguageResult:
    lang: str
    name: str
    status: str  # "ok" | "error"
    file_suffix: str
    markdown: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0


@dataclass
class TranslateAllResult:
    results: list[TranslateAllLanguageResult]
    succeeded: int
    failed: int
    duration_ms: float


def build_nav_bar(
    languages: list[TargetLanguage],
    succeeded: set[str],
    current_lang_code: Optional[str] = None,
) -> str:
    """Build a language nav bar HTML block."""
    links: list[str] = []
    for lang in languages:
        if lang.code not in succeeded:
            continue
        file = f"README.{lang.file or lang.code}.md"
        if lang.code == current_lang_code:
            links.append('<a href="README.md">English</a>')
        else:
            links.append(f'<a href="{file}">{lang.label}</a>')
    return f'<p align="center">\n  {" | ".join(links)}\n</p>'


def inject_nav_bar(markdown: str, nav_bar: str) -> str:
    """Inject a nav bar at the top, replacing any existing nav bars."""
    lines = markdown.split("\n")
    i = 0

    while i < len(lines):
        if lines[i].strip() == "":
            i += 1
            continue
        if re.match(r'^<p\s+align="center">', lines[i].strip()):
            is_nav = False
            for j in range(i, min(i + 5, len(lines))):
                if re.search(r'href="README\.\w', lines[j]) or re.search(r'href="README\.md"', lines[j]):
                    is_nav = True
                    break
                if "</p>" in lines[j]:
                    break
            if is_nav:
                while i < len(lines) and "</p>" not in lines[i]:
                    i += 1
                i += 1
                continue
        break

    rest = lines[i:]
    return nav_bar + "\n\n" + "\n".join(rest)


async def translate_all(
    markdown: str,
    source_lang: str = "en",
    target_langs: Optional[list[str]] = None,
    model: Optional[str] = None,
    concurrency: int = 2,
    nav_bar: bool = True,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
) -> TranslateAllResult:
    """Translate markdown content into multiple languages concurrently."""
    concurrency = min(3, max(1, concurrency))

    targets = TRANSLATE_ALL_LANGUAGES
    if target_langs:
        codes = {c.lower() for c in target_langs}
        targets = [l for l in TRANSLATE_ALL_LANGUAGES if l.code in codes]

    start = time.time()
    results: list[TranslateAllLanguageResult] = []
    completed = 0

    sem = Semaphore(concurrency)

    async def translate_lang(lang: TargetLanguage) -> TranslateAllLanguageResult:
        nonlocal completed
        lang_start = time.time()
        try:
            async with sem:
                opts = TranslateMarkdownOptions(model=model, cache=False)
                result = await translate_markdown(markdown, source_lang, lang.code, opts)
                lang_result = TranslateAllLanguageResult(
                    lang=lang.code,
                    name=lang.name,
                    status="ok",
                    file_suffix=lang.file or lang.code,
                    markdown=result.markdown,
                    duration_ms=(time.time() - lang_start) * 1000,
                )
        except Exception as err:
            lang_result = TranslateAllLanguageResult(
                lang=lang.code,
                name=lang.name,
                status="error",
                file_suffix=lang.file or lang.code,
                error=str(err),
                duration_ms=(time.time() - lang_start) * 1000,
            )
        finally:
            completed += 1
            if on_progress:
                on_progress(completed, len(targets), lang.name)

        results.append(lang_result)
        return lang_result

    await asyncio.gather(*(translate_lang(lang) for lang in targets))

    # Sort results to match language order
    lang_order = {l.code: i for i, l in enumerate(targets)}
    results.sort(key=lambda r: lang_order.get(r.lang, 0))

    # Inject nav bars
    if nav_bar:
        succeeded_codes = {r.lang for r in results if r.status == "ok"}
        if succeeded_codes:
            for r in results:
                if r.status == "ok" and r.markdown:
                    nav = build_nav_bar(targets, succeeded_codes, r.lang)
                    r.markdown = inject_nav_bar(r.markdown, nav)

    succeeded = sum(1 for r in results if r.status == "ok")
    failed = sum(1 for r in results if r.status == "error")

    return TranslateAllResult(
        results=results,
        succeeded=succeeded,
        failed=failed,
        duration_ms=(time.time() - start) * 1000,
    )
