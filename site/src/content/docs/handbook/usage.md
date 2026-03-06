---
title: Library Usage
description: Python API for text, markdown, and multi-language translation.
sidebar:
  order: 2
---

## Simple text translation

```python
from pypolyglot import translate

result = await translate("Hello world", "en", "ja")
print(result.translation)  # こんにちは世界
```

The `translate` function handles chunking, batching, and retry automatically. For long text, it splits into segments, translates each, and reassembles the result.

## Markdown translation

```python
from pypolyglot import translate_markdown

md = """## Features

Local GPU translation with **zero cloud dependency**.

```python
result = await translate("Hello", "en", "ja")
```
"""

result = await translate_markdown(md, "en", "fr")
print(result.markdown)
```

Markdown translation preserves:
- Code blocks (fenced and inline)
- Tables
- HTML tags and attributes
- URLs, badges, and image references
- Heading structure

## Multi-language translation

Translate into 7 languages at once:

```python
from pypolyglot import translate_all

result = await translate_all(md, source_lang="en")
for r in result.results:
    print(f"{r.name}: {r.status} ({r.duration_ms:.0f}ms)")
```

Default languages: Japanese, Chinese (Simplified), Spanish, French, Hindi, Italian, Portuguese (BR).

Target specific languages:

```python
result = await translate_all(md, target_langs=["ja", "es", "fr"])
```

## Translation options

### Custom model

```python
from pypolyglot import translate, TranslateOptions

result = await translate("Hello", "en", "ja",
    TranslateOptions(model="translategemma:4b"))
```

### Custom glossary

Override translations for specific terms:

```python
from pypolyglot import translate, TranslateOptions, GlossaryEntry

result = await translate("Deploy the Widget", "en", "ja",
    TranslateOptions(glossary=[
        GlossaryEntry("Widget", {"ja": "ウィジェット"})
    ]))
```

polyglot-gpu includes a built-in software glossary with 12 technical terms (Architecture, Pipeline, Deploy, Library, Framework, Build, Release, Branch, Repository, Merge, Token, Adoption). These are injected automatically when the terms appear in the source text.

### Streaming

```python
result = await translate("Hello world", "en", "ja",
    TranslateOptions(on_token=lambda t: print(t, end="")))
```

### Caching

Segment-level caching is enabled by default. Cache uses Levenshtein fuzzy matching — if a segment is similar enough to a previously translated one, the cached translation is reused.

```python
from pypolyglot import translate_markdown, TranslateMarkdownOptions

# Disable caching
result = await translate_markdown(md, "en", "ja",
    TranslateMarkdownOptions(cache=False))
```

Cache files are stored as `.polyglot-cache.json` in the working directory.
