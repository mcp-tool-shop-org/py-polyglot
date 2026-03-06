---
title: Architecture
description: How the 12 modules work together inside polyglot-gpu.
sidebar:
  order: 5
---

polyglot-gpu is organized as 12 Python modules, each with a single responsibility.

## Module map

```
MCP Client (Claude Code, etc.)
      │ MCP protocol (stdio)
      ▼
┌──────────────────┐
│   server.py      │  5 MCP tools (FastMCP)
├──────────────────┤
│  translate.py    │  Chunking, batching, streaming
│  markdown.py     │  Markdown segmentation + cleanup
│  translate_all   │  Multi-language orchestrator
│  semaphore.py    │  GPU-safe concurrency control
│  validate.py     │  Output validation
├──────────────────┤
│   ollama.py      │  httpx pooled client → Ollama
│   cache.py       │  Segment cache + fuzzy memory
│  glossary.py     │  Software term dictionary
│ languages.py     │  57 language definitions
│   polish.py      │  Post-translation cleanup
│   errors.py      │  Structured error codes
└──────────────────┘
      │ HTTP (httpx)
      ▼
   Ollama + TranslateGemma (GPU)
```

## Request flow

1. **server.py** receives an MCP tool call and dispatches to the appropriate handler
2. **translate.py** splits text into chunks, builds prompts with glossary hints, and calls Ollama
3. **ollama.py** sends the request via a pooled httpx connection to `localhost:11434`
4. **validate.py** checks the response for quality issues (language leakage, truncation)
5. **polish.py** cleans up common model artifacts (stray quotes, formatting noise)
6. **cache.py** stores the segment result for future fuzzy matching

## Key design decisions

### Connection pooling

The Ollama client reuses a single `httpx.AsyncClient` across all requests instead of creating a new connection per call. This reduces TCP handshake overhead and improves throughput for batch translations.

### Semaphore concurrency

A custom `Semaphore` class wraps `asyncio.Semaphore` with an active-count tracker protected by `asyncio.Lock`. This prevents multiple GPU-bound requests from exhausting VRAM. The semaphore supports both explicit acquire/release and `async with` context manager patterns.

### Markdown segmentation

`markdown.py` splits markdown into translatable segments and structural segments. Code blocks, HTML tags, URLs, and badges are classified as structural and passed through untranslated. Only prose segments go through the translation pipeline.

### Fuzzy cache matching

`cache.py` uses Levenshtein distance to match incoming segments against cached translations. This handles minor text edits (typo fixes, punctuation changes) without re-translating the entire segment.

### Structured errors

`errors.py` defines `PolyglotError` with typed error codes, human-readable messages, optional hints, and a retryable flag. The `friendly_error` function converts any exception into a user-facing message.

## Test coverage

100 tests across 10 test files covering all modules. Tests use pytest with pytest-asyncio for async test support.
