---
title: Security
description: Threat model and privacy guarantees for polyglot-gpu.
sidebar:
  order: 6
---

## Privacy by design

polyglot-gpu runs entirely on your local machine. No data is sent to any external service.

## Threat model

### Data touched
- Text sent to the local Ollama API at `localhost:11434`
- `.polyglot-cache.json` segment cache in the working directory

### Data NOT touched
- No files outside the working directory
- No browser data, OS credentials, or system files
- No environment variables beyond `POLYGLOT_MODEL` and `POLYGLOT_CONCURRENCY`

### Network
- HTTP to `localhost:11434` only
- Zero external or internet egress
- No DNS lookups, no telemetry endpoints

### No telemetry
- No data collection or transmission of any kind
- No usage analytics, crash reports, or phone-home behavior

### No secrets
- No API keys, tokens, or credentials required or stored
- No authentication mechanism — Ollama runs locally without auth

## Cache security

The segment cache (`.polyglot-cache.json`) stores translated text segments locally. Path traversal protection uses Python's `Path.relative_to()` to prevent cache files from escaping the intended directory.

If your source text contains sensitive content, be aware that translations are cached in plaintext. Delete the cache file to remove stored translations:

```bash
rm .polyglot-cache.json
```

## Dependency security

polyglot-gpu depends on:
- `httpx` — HTTP client for Ollama communication
- `mcp[cli]` — FastMCP server framework
- `python-Levenshtein` — Fuzzy string matching for cache

CI runs `pip-audit` on every push to detect known vulnerabilities in dependencies.

## Reporting vulnerabilities

Report security issues to: 64996768+mcp-tool-shop@users.noreply.github.com
