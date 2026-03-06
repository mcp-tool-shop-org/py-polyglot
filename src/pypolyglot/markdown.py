"""
Markdown-aware translation engine.

Translates markdown documents while preserving structure: code blocks,
HTML elements, tables, URLs, and formatting are left intact.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from .cache import (
    TranslationCache,
    cache_key,
    clear_cache,
    create_cache,
    get_cached,
    get_fuzzy_cached,
    load_cache,
    prune_cache,
    save_cache,
    set_cached,
)
from .errors import ErrorCode, PolyglotError
from .languages import resolve_language
from .translate import BatchItem, TranslateBatchOptions, translate_batch
from .validate import validate_translation


# --- Types ---

@dataclass
class Segment:
    type: str  # "protected" | "html-tagline" | "heading" | "text" | "table"
    text: str
    prefix: Optional[str] = None
    _parsed: Optional[list] = field(default=None, repr=False)


@dataclass
class CellData:
    translatable: bool
    original: str


@dataclass
class TranslateMarkdownOptions(TranslateBatchOptions):
    cache: bool = True
    cache_clear: bool = False
    file_path: Optional[str] = None
    on_progress: Optional[Callable[[int, int], None]] = None


@dataclass
class TranslateMarkdownResult:
    markdown: str
    segments: int
    cached: int
    translated: int
    deduplicated: int
    fuzzy_matched: int
    ollama_calls: int
    duration_ms: float
    warnings: list[str] = field(default_factory=list)


# --- Segmentation ---

def segment_markdown(md: str) -> list[Segment]:
    """Break a markdown document into translatable and protected segments."""
    segments: list[Segment] = []
    lines = md.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if re.match(r"^```", line):
            block = [line]
            i += 1
            while i < len(lines) and not re.match(r"^```", lines[i]):
                block.append(lines[i])
                i += 1
            if i < len(lines):
                block.append(lines[i])
                i += 1
            segments.append(Segment(type="protected", text="\n".join(block)))
            continue

        # HTML tagline
        if re.match(r"^<p[^>]*><strong>[^<]+</strong></p>", line.strip()):
            segments.append(Segment(type="html-tagline", text=line))
            i += 1
            continue

        # HTML block
        if re.match(r"^<[a-z]", line.strip(), re.IGNORECASE):
            block = [line]
            i += 1
            while i < len(lines) and lines[i].strip() != "" and not re.match(r"^(---|##)", lines[i]):
                block.append(lines[i])
                i += 1
            segments.append(Segment(type="protected", text="\n".join(block)))
            continue

        # Horizontal rule
        if re.match(r"^---\s*$", line):
            segments.append(Segment(type="protected", text=line))
            i += 1
            continue

        # Empty line
        if line.strip() == "":
            segments.append(Segment(type="protected", text=""))
            i += 1
            continue

        # Table
        if re.match(r"^\|", line):
            table_lines: list[str] = []
            while i < len(lines) and re.match(r"^\|", lines[i]):
                table_lines.append(lines[i])
                i += 1
            segments.append(Segment(type="table", text="\n".join(table_lines)))
            continue

        # Heading
        if re.match(r"^#{1,6}\s", line):
            m = re.match(r"^(#{1,6}\s+)(.*)", line)
            if m:
                segments.append(Segment(type="heading", prefix=m.group(1), text=m.group(2)))
            else:
                segments.append(Segment(type="text", text=line))
            i += 1
            continue

        # Block quote
        if re.match(r"^>\s", line):
            block = []
            while i < len(lines) and re.match(r"^>\s?", lines[i]):
                block.append(lines[i])
                i += 1
            segments.append(Segment(type="text", text="\n".join(block)))
            continue

        # Regular paragraph
        para: list[str] = []
        while (
            i < len(lines)
            and lines[i].strip() != ""
            and not re.match(r"^(```|<[a-z]|---|#{1,6}\s|\||>\s)", lines[i], re.IGNORECASE)
        ):
            para.append(lines[i])
            i += 1
        if para:
            segments.append(Segment(type="text", text="\n".join(para)))

    return segments


# --- Table parsing ---

def is_translatable_cell(trimmed: str) -> bool:
    """Check if a table cell contains translatable prose."""
    if re.match(r"^`[^`]+`$", trimmed):
        return False
    if re.match(r"^(`[^`]+`[,\s]*)+$", trimmed):
        return False
    if re.match(r"^@\w+/", trimmed):
        return False
    if re.match(r"^\*\*[A-Za-z]", trimmed) and len(trimmed) < 30:
        return False
    if re.match(r"^[\d.]+$", trimmed):
        return False
    if re.match(r"^\[.*\]\(.*\)$", trimmed):
        return False
    if trimmed in ("—", "-"):
        return False
    if len(trimmed) <= 2:
        return False
    if not re.search(r"[A-Za-z\u00C0-\u024F]", trimmed):
        return False
    return True


def parse_table(table_text: str):
    """Parse a markdown table into rows/cells, identifying translatable cells."""
    rows = table_text.split("\n")
    parsed: list[dict] = []
    translatable_cells: list[dict] = []

    for row_text in rows:
        if re.match(r"^\|[\s\-:|]+\|$", row_text):
            parsed.append({"type": "separator", "raw": row_text})
            continue
        cells = row_text.split("|")[1:-1]
        cell_data: list[CellData] = []
        for c_idx, cell in enumerate(cells):
            trimmed = cell.strip()
            if is_translatable_cell(trimmed):
                translatable_cells.append({
                    "row_idx": len(parsed),
                    "cell_idx": c_idx,
                    "text": trimmed,
                })
                cell_data.append(CellData(translatable=True, original=cell))
            else:
                cell_data.append(CellData(translatable=False, original=cell))
        parsed.append({"type": "data", "cells": cell_data})

    return parsed, translatable_cells


def reassemble_table(parsed: list[dict], translated_map: dict[str, str]) -> str:
    """Reassemble a table from parsed data with translated cells injected."""
    rows: list[str] = []
    for row_idx, row in enumerate(parsed):
        if row["type"] == "separator":
            rows.append(row["raw"])
            continue
        cells = []
        for c_idx, c in enumerate(row["cells"]):
            key = f"{row_idx}:{c_idx}"
            if c.translatable and key in translated_map:
                cells.append(f" {translated_map[key]} ")
            else:
                cells.append(c.original)
        rows.append("|" + "|".join(cells) + "|")
    return "\n".join(rows)


# --- Translation cleaning ---

_OR_PATTERNS = [
    re.compile(r"\nまたは\n.*", re.DOTALL),
    re.compile(r"\n또는\n.*", re.DOTALL),
    re.compile(r"\no\n(?=[A-Z]).*", re.DOTALL),
    re.compile(r"\nou\n.*", re.DOTALL),
    re.compile(r"\noder\n.*", re.DOTALL),
    re.compile(r"\nили\n.*", re.DOTALL),
    re.compile(r"\nया\n.*", re.DOTALL),
    re.compile(r"\nveya\n.*", re.DOTALL),
    re.compile(r"\nหรือ\n.*", re.DOTALL),
    re.compile(r"\nhoặc\n.*", re.DOTALL),
    re.compile(r"\natau\n.*", re.DOTALL),
    re.compile(r"\nof\n(?=[A-Z]).*", re.DOTALL),
]


def clean_translation(text: str, is_heading: bool = False) -> str:
    cleaned = text
    for pat in _OR_PATTERNS:
        cleaned = pat.sub("", cleaned)
    if is_heading:
        cleaned = re.sub(r"[。．.]\s*$", "", cleaned)
    return cleaned.strip()


# --- HTML tagline helpers ---

def extract_tagline_text(line: str) -> Optional[str]:
    m = re.search(r"<strong>([^<]+)</strong>", line)
    return m.group(1) if m else None


def rebuild_tagline(original_line: str, translated_text: str) -> str:
    return re.sub(
        r"(<strong>)[^<]+(</strong>)",
        rf"\g<1>{translated_text}\g<2>",
        original_line,
    )


# --- Core translate function ---

async def translate_markdown(
    markdown: str,
    source_lang: str,
    target_lang: str,
    options: Optional[TranslateMarkdownOptions] = None,
) -> TranslateMarkdownResult:
    """Translate a markdown document while preserving its structure."""
    opts = options or TranslateMarkdownOptions()

    source = resolve_language(source_lang)
    if not source:
        raise PolyglotError(
            code=ErrorCode.UNSUPPORTED_LANGUAGE,
            message=f'Unsupported source language: "{source_lang}".',
            hint="Use the list_languages tool to see all 57 supported languages.",
            retryable=False,
        )

    target = resolve_language(target_lang)
    if not target:
        raise PolyglotError(
            code=ErrorCode.UNSUPPORTED_LANGUAGE,
            message=f'Unsupported target language: "{target_lang}".',
            hint="Use the list_languages tool to see all 57 supported languages.",
            retryable=False,
        )

    start = time.time()
    warnings: list[str] = []
    use_cache = opts.cache
    model_str = opts.model or "translategemma:12b"

    # Set up cache
    if use_cache and opts.file_path:
        cache = load_cache(opts.file_path)
        if opts.cache_clear:
            clear_cache(cache)
            save_cache(opts.file_path, cache)
        else:
            prune_cache(cache)
    else:
        cache = create_cache()

    # Segment
    segments = segment_markdown(markdown)

    # Collect all translatable items
    @dataclass
    class BatchEntry:
        seg_index: int
        kind: str
        text: str
        cache_hit: Optional[str] = None
        fuzzy_hit: bool = False
        table_key: Optional[str] = None

    batch_items: list[BatchEntry] = []

    for s, seg in enumerate(segments):
        if seg.type == "protected":
            continue

        if seg.type == "html-tagline":
            inner_text = extract_tagline_text(seg.text)
            if inner_text:
                key = cache_key(inner_text, target_lang, model_str)
                cached = get_cached(cache, key) if use_cache else None
                fuzzy = get_fuzzy_cached(cache, inner_text, target_lang, model_str) if (not cached and use_cache) else None
                entry = BatchEntry(seg_index=s, kind="text", text=inner_text)
                if cached:
                    entry.cache_hit = cached
                elif fuzzy:
                    entry.cache_hit = fuzzy["translation"]
                    entry.fuzzy_hit = True
                batch_items.append(entry)
            continue

        if seg.type == "heading":
            key = cache_key(seg.text, target_lang, model_str)
            cached = get_cached(cache, key) if use_cache else None
            fuzzy = get_fuzzy_cached(cache, seg.text, target_lang, model_str) if (not cached and use_cache) else None
            entry = BatchEntry(seg_index=s, kind="heading", text=seg.text)
            if cached:
                entry.cache_hit = cached
            elif fuzzy:
                entry.cache_hit = fuzzy["translation"]
                entry.fuzzy_hit = True
            batch_items.append(entry)
            continue

        if seg.type == "text":
            if re.match(r"^`[^`]+`$", seg.text.strip()):
                continue
            key = cache_key(seg.text, target_lang, model_str)
            cached = get_cached(cache, key) if use_cache else None
            fuzzy = get_fuzzy_cached(cache, seg.text, target_lang, model_str) if (not cached and use_cache) else None
            entry = BatchEntry(seg_index=s, kind="text", text=seg.text)
            if cached:
                entry.cache_hit = cached
            elif fuzzy:
                entry.cache_hit = fuzzy["translation"]
                entry.fuzzy_hit = True
            batch_items.append(entry)
            continue

        if seg.type == "table":
            parsed, translatable_cells = parse_table(seg.text)
            seg._parsed = parsed
            for cell in translatable_cells:
                key = cache_key(cell["text"], target_lang, model_str)
                cached = get_cached(cache, key) if use_cache else None
                fuzzy = get_fuzzy_cached(cache, cell["text"], target_lang, model_str) if (not cached and use_cache) else None
                table_key = f"{cell['row_idx']}:{cell['cell_idx']}"
                entry = BatchEntry(seg_index=s, kind="cell", text=cell["text"], table_key=table_key)
                if cached:
                    entry.cache_hit = cached
                elif fuzzy:
                    entry.cache_hit = fuzzy["translation"]
                    entry.fuzzy_hit = True
                batch_items.append(entry)
            continue

    # Split into hits and misses
    misses = [b for b in batch_items if not b.cache_hit]
    cache_hits = sum(1 for b in batch_items if b.cache_hit and not b.fuzzy_hit)
    fuzzy_hits = sum(1 for b in batch_items if b.fuzzy_hit)

    # Dedup misses
    unique_texts: dict[str, int] = {}
    unique_items: list[BatchItem] = []
    miss_to_unique: list[int] = []

    for m in misses:
        if m.text in unique_texts:
            miss_to_unique.append(unique_texts[m.text])
        else:
            idx = len(unique_items)
            unique_texts[m.text] = idx
            unique_items.append(BatchItem(text=m.text, kind=m.kind))
            miss_to_unique.append(idx)

    deduplicated = len(misses) - len(unique_items)

    # Report progress for cache hits
    total_items = len(batch_items)
    completed_items = cache_hits + fuzzy_hits
    if opts.on_progress and completed_items > 0:
        opts.on_progress(completed_items, total_items)

    # Translate unique misses
    unique_translations: list[str] = []
    ollama_calls = 0

    if unique_items:
        batch_opts = TranslateBatchOptions(
            model=opts.model,
            temperature=opts.temperature,
            ollama_url=opts.ollama_url,
            glossary=opts.glossary,
            software_glossary=opts.software_glossary,
            do_polish=opts.do_polish,
            batch_char_limit=opts.batch_char_limit,
        )
        result = await translate_batch(unique_items, source_lang, target_lang, batch_opts)
        unique_translations = result.translations
        ollama_calls = result.ollama_calls

        # Cache the results
        if use_cache:
            for i, item in enumerate(unique_items):
                key = cache_key(item.text, target_lang, model_str)
                set_cached(cache, key, unique_translations[i], model_str, item.text, target_lang)

        if opts.on_progress:
            opts.on_progress(total_items, total_items)

    # Validate and build maps
    translation_map: dict[int, str] = {}
    table_translation_maps: dict[int, dict[str, str]] = {}

    miss_idx = 0
    for item in batch_items:
        if item.cache_hit:
            translated = item.cache_hit
        else:
            translated = unique_translations[miss_to_unique[miss_idx]]
            miss_idx += 1

        try:
            validation = validate_translation(item.text, translated, source_lang, target_lang)
            if not validation.valid:
                for w in validation.warnings:
                    warnings.append(f'[segment "{item.text[:40]}…"]: {w}')
        except PolyglotError:
            warnings.append(f'[segment "{item.text[:40]}…"]: Empty translation, using source text as fallback.')
            translated = item.text

        cleaned = clean_translation(translated, item.kind == "heading")

        if item.table_key is not None:
            if item.seg_index not in table_translation_maps:
                table_translation_maps[item.seg_index] = {}
            table_translation_maps[item.seg_index][item.table_key] = cleaned
        else:
            translation_map[item.seg_index] = cleaned

    # Assemble output
    output: list[str] = []
    for s, seg in enumerate(segments):
        if seg.type == "protected":
            output.append(seg.text)
        elif seg.type == "html-tagline":
            if s in translation_map:
                output.append(rebuild_tagline(seg.text, translation_map[s]))
            else:
                output.append(seg.text)
        elif seg.type == "heading":
            output.append((seg.prefix or "") + translation_map.get(s, seg.text))
        elif seg.type == "text":
            output.append(translation_map.get(s, seg.text))
        elif seg.type == "table":
            t_map = table_translation_maps.get(s, {})
            if seg._parsed:
                output.append(reassemble_table(seg._parsed, t_map))
            else:
                output.append(seg.text)

    # Save cache
    if use_cache and opts.file_path:
        save_cache(opts.file_path, cache)

    return TranslateMarkdownResult(
        markdown="\n".join(output),
        segments=len(batch_items),
        cached=cache_hits,
        translated=len(unique_items),
        deduplicated=deduplicated,
        fuzzy_matched=fuzzy_hits,
        ollama_calls=ollama_calls,
        duration_ms=(time.time() - start) * 1000,
        warnings=warnings,
    )
