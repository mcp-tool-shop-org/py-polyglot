"""
Core translation logic — builds prompts, calls Ollama, handles chunking.
Includes glossary injection, post-translation polish, and batch mode.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from .errors import ErrorCode, PolyglotError
from .glossary import SOFTWARE_GLOSSARY, GlossaryEntry, build_glossary_hint
from .languages import Language, resolve_language
from .ollama import OllamaClient, OllamaGenerateRequest, StreamCallback
from .polish import polish
from .validate import validate_translation

DEFAULT_MODEL = os.environ.get("POLYGLOT_MODEL", "translategemma:12b")
BATCH_SEPARATOR = "\n---POLYGLOT_SEP---\n"


def get_chunk_size(model: str) -> int:
    """Chunk size varies by model — bigger models handle more context."""
    if ":2b" in model or ":4b" in model:
        return 2000
    if ":27b" in model:
        return 6000
    return 4000  # 12b and default


@dataclass
class TranslateOptions:
    model: Optional[str] = None
    temperature: Optional[float] = None
    ollama_url: Optional[str] = None
    glossary: Optional[list[GlossaryEntry]] = None
    software_glossary: bool = True
    do_polish: bool = True
    on_token: Optional[StreamCallback] = None
    do_validate: bool = True


@dataclass
class TranslateResult:
    translation: str
    source_language: Language
    target_language: Language
    model: str
    chunks: int
    duration_ms: float
    warnings: list[str] = field(default_factory=list)


@dataclass
class BatchItem:
    text: str
    kind: str = "text"  # "heading" | "text" | "cell"


@dataclass
class TranslateBatchOptions(TranslateOptions):
    batch_char_limit: Optional[int] = None


@dataclass
class TranslateBatchResult:
    translations: list[str]
    model: str
    ollama_calls: int
    duration_ms: float


def build_prompt(source: Language, target: Language, text: str, glossary_hint: str) -> str:
    """Build the TranslateGemma prompt."""
    return (
        f"You are a professional {source.name} ({source.code}) to {target.name} ({target.code}) translator. "
        f"Your goal is to accurately convey the meaning and nuances of the original {source.name} text "
        f"while adhering to {target.name} grammar, vocabulary, and cultural sensitivities.\n"
        f"Produce only the {target.name} translation, without any additional explanations or commentary."
        f"{glossary_hint} Please translate the following {source.name} text into {target.name}:\n\n\n"
        f"{text}"
    )


def build_batch_prompt(source: Language, target: Language, joined_text: str, glossary_hint: str) -> str:
    """Build a batch prompt with separator instructions."""
    return (
        f"You are a professional {source.name} ({source.code}) to {target.name} ({target.code}) translator. "
        f"Your goal is to accurately convey the meaning and nuances of the original {source.name} text "
        f"while adhering to {target.name} grammar, vocabulary, and cultural sensitivities.\n"
        f"Produce only the {target.name} translation, without any additional explanations or commentary.\n"
        f'IMPORTANT: The text contains separator lines "---POLYGLOT_SEP---". '
        f"Keep each separator exactly as-is in your output. Do NOT translate, remove, or modify the separators."
        f"{glossary_hint} Please translate the following {source.name} text into {target.name}:\n\n\n"
        f"{joined_text}"
    )


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Split text into chunks at paragraph/sentence boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break

        # Try to split at paragraph boundary
        split_at = remaining.rfind("\n\n", 0, max_chars)
        if split_at < max_chars * 0.3:
            # Try sentence boundary
            split_at = remaining.rfind(". ", 0, max_chars)
            if split_at < max_chars * 0.3:
                # Try any newline
                split_at = remaining.rfind("\n", 0, max_chars)
                if split_at < max_chars * 0.3:
                    split_at = max_chars
            if split_at > 0 and remaining[split_at] == ".":
                split_at += 1

        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()

    return chunks


async def _resolve_setup(
    source_lang: str,
    target_lang: str,
    options: TranslateOptions,
):
    """Resolve languages and ensure Ollama + model are ready."""
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

    if source.code == target.code:
        raise PolyglotError(
            code=ErrorCode.SAME_LANGUAGE,
            message="Source and target languages must be different.",
            hint="Nothing to translate — source and target are the same.",
            retryable=False,
        )

    model = options.model or DEFAULT_MODEL
    client = OllamaClient(options.ollama_url or "http://localhost:11434")

    if not await client.ensure_running():
        raise PolyglotError(
            code=ErrorCode.OLLAMA_UNAVAILABLE,
            message="Could not start Ollama.",
            hint="Install it from https://ollama.com then try again.",
            retryable=True,
        )

    if not await client.ensure_model(model):
        raise PolyglotError(
            code=ErrorCode.MODEL_PULL_FAILED,
            message=f'Could not pull model "{model}".',
            hint=f"Run manually: ollama pull {model}",
            retryable=True,
        )

    glossary_entries: list[GlossaryEntry] = []
    if options.software_glossary:
        glossary_entries.extend(SOFTWARE_GLOSSARY)
    if options.glossary:
        glossary_entries.extend(options.glossary)

    return source, target, model, client, glossary_entries


async def translate(
    text: str,
    source_lang: str,
    target_lang: str,
    options: Optional[TranslateOptions] = None,
) -> TranslateResult:
    """Translate text using TranslateGemma via Ollama."""
    opts = options or TranslateOptions()
    source, target, model, client, glossary_entries = await _resolve_setup(
        source_lang, target_lang, opts
    )

    chunks = chunk_text(text.strip(), get_chunk_size(model))
    start = time.time()
    translations: list[str] = []
    warnings: list[str] = []
    use_stream = opts.on_token is not None

    for chunk in chunks:
        glossary_hint = build_glossary_hint(chunk, target.code, glossary_entries)
        prompt = build_prompt(source, target, chunk, glossary_hint)

        req = OllamaGenerateRequest(
            model=model,
            prompt=prompt,
            temperature=opts.temperature if opts.temperature is not None else 0.1,
        )

        if use_stream:
            response = await client.generate_stream(req, opts.on_token)  # type: ignore[arg-type]
        else:
            response = await client.generate(req)

        translated = response.response.strip()
        if opts.do_polish:
            translated = polish(translated)

        if opts.do_validate:
            try:
                validation = validate_translation(chunk, translated, source_lang, target_lang)
                warnings.extend(validation.warnings)
            except PolyglotError:
                warnings.append("Chunk translation returned empty output — using source text.")
                translated = chunk

        translations.append(translated)

    return TranslateResult(
        translation="\n\n".join(translations),
        source_language=source,
        target_language=target,
        model=model,
        chunks=len(chunks),
        duration_ms=(time.time() - start) * 1000,
        warnings=warnings,
    )


async def translate_batch(
    items: list[BatchItem],
    source_lang: str,
    target_lang: str,
    options: Optional[TranslateBatchOptions] = None,
) -> TranslateBatchResult:
    """Translate multiple text segments in as few Ollama calls as possible."""
    opts = options or TranslateBatchOptions()
    if not items:
        return TranslateBatchResult(
            translations=[], model=opts.model or DEFAULT_MODEL, ollama_calls=0, duration_ms=0
        )

    source, target, model, client, glossary_entries = await _resolve_setup(
        source_lang, target_lang, opts
    )

    batch_limit = opts.batch_char_limit or get_chunk_size(model)
    start = time.time()
    results: list[Optional[str]] = [None] * len(items)
    ollama_calls = 0

    batch_start = 0
    while batch_start < len(items):
        batch_items: list[dict] = []
        batch_size = 0

        for i in range(batch_start, len(items)):
            added_size = len(items[i].text) + (len(BATCH_SEPARATOR) if batch_items else 0)
            if batch_size + added_size > batch_limit and batch_items:
                break
            batch_items.append({"index": i, "text": items[i].text})
            batch_size += added_size

        if len(batch_items) == 1:
            # Single item — use normal prompt
            item = batch_items[0]
            glossary_hint = build_glossary_hint(item["text"], target.code, glossary_entries)
            prompt = build_prompt(source, target, item["text"], glossary_hint)
            req = OllamaGenerateRequest(
                model=model, prompt=prompt,
                temperature=opts.temperature if opts.temperature is not None else 0.1,
            )
            response = await client.generate(req)
            ollama_calls += 1
            translated = response.response.strip()
            if opts.do_polish:
                translated = polish(translated)
            results[item["index"]] = translated
        else:
            # Multiple items — join with separator
            joined_text = BATCH_SEPARATOR.join(b["text"] for b in batch_items)
            glossary_hint = build_glossary_hint(joined_text, target.code, glossary_entries)
            prompt = build_batch_prompt(source, target, joined_text, glossary_hint)
            req = OllamaGenerateRequest(
                model=model, prompt=prompt,
                temperature=opts.temperature if opts.temperature is not None else 0.1,
            )
            response = await client.generate(req)
            ollama_calls += 1

            output_parts = response.response.split("---POLYGLOT_SEP---")

            if len(output_parts) == len(batch_items):
                for j, bi in enumerate(batch_items):
                    translated = output_parts[j].strip()
                    if opts.do_polish:
                        translated = polish(translated)
                    results[bi["index"]] = translated
            else:
                # Fallback: re-translate each item individually
                for bi in batch_items:
                    hint = build_glossary_hint(bi["text"], target.code, glossary_entries)
                    fallback_prompt = build_prompt(source, target, bi["text"], hint)
                    req = OllamaGenerateRequest(
                        model=model, prompt=fallback_prompt,
                        temperature=opts.temperature if opts.temperature is not None else 0.1,
                    )
                    fallback_response = await client.generate(req)
                    ollama_calls += 1
                    translated = fallback_response.response.strip()
                    if opts.do_polish:
                        translated = polish(translated)
                    results[bi["index"]] = translated

        batch_start += len(batch_items)

    return TranslateBatchResult(
        translations=[r or "" for r in results],
        model=model,
        ollama_calls=ollama_calls,
        duration_ms=(time.time() - start) * 1000,
    )
