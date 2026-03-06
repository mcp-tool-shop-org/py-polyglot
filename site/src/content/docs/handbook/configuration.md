---
title: Configuration
description: Models, environment variables, and performance tuning.
sidebar:
  order: 4
---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | Default Ollama model for translation |
| `POLYGLOT_CONCURRENCY` | `1` | Max concurrent Ollama API calls |

## Model selection

Three TranslateGemma model sizes are available:

| Model | Parameters | VRAM | Use case |
|-------|-----------|------|----------|
| `translategemma:4b` | 4 billion | 3.3 GB | Quick translations, limited GPU |
| `translategemma:12b` | 12 billion | 8.1 GB | General use, balanced quality/speed |
| `translategemma:27b` | 27 billion | 17 GB | Maximum quality, large GPU required |

Set the default model via environment variable:

```bash
export POLYGLOT_MODEL=translategemma:4b
```

Or override per-request:

```python
from pypolyglot import translate, TranslateOptions

result = await translate("Hello", "en", "ja",
    TranslateOptions(model="translategemma:27b"))
```

## Concurrency

The concurrency setting controls how many Ollama API calls run simultaneously. This is GPU-bound — running too many concurrent calls can cause VRAM exhaustion.

```bash
export POLYGLOT_CONCURRENCY=2
```

Recommendations:
- **1** (default) — Safe for any GPU, sequential processing
- **2** — Good for 12+ GB VRAM with the 4b model
- **3** — Maximum, only for 24+ GB VRAM

The semaphore prevents more than `concurrency` calls from hitting the GPU at once. Additional requests queue until a slot opens.

## Glossary customization

The built-in software glossary covers 12 technical terms. Add your own:

```python
from pypolyglot import translate, TranslateOptions, GlossaryEntry

custom_glossary = [
    GlossaryEntry("Widget", {"ja": "ウィジェット", "zh": "小部件"}),
    GlossaryEntry("Dashboard", {"ja": "ダッシュボード", "zh": "仪表盘"}),
]

result = await translate(text, "en", "ja",
    TranslateOptions(glossary=custom_glossary))
```

Glossary entries only apply when the term appears in the source text AND the target language has a translation defined.

## Cache behavior

Translation cache stores segment-level results in `.polyglot-cache.json`. It uses Levenshtein distance for fuzzy matching — segments that are similar enough to a cached entry reuse the cached translation.

Cache is per-directory and per-language pair. To clear it, delete the cache file:

```bash
rm .polyglot-cache.json
```
