# Changelog

## 1.0.2 (2026-03-06)

- Renamed PyPI distribution from `py-polyglot` to `polyglot-gpu` (import name `pypolyglot` unchanged)
- CLI entry point renamed to `polyglot-gpu`

## 1.0.1 (2026-03-06)

- Shipcheck compliance: verify script, dependency audit, dependabot
- Landing page via @mcptoolshop/site-theme
- Translated READMEs (7 languages)

## 1.0.0 (2026-03-06)

- Initial release — Python port of polyglot-mcp
- 57 languages via TranslateGemma + Ollama
- Dual-use: Python library (`pip install polyglot-gpu`) + MCP server
- Core translation with chunking, batching, retry, and validation
- Markdown-aware translation preserving code blocks, tables, HTML
- Multi-language orchestrator with concurrent translation
- Segment-level caching with fuzzy matching (translation memory)
- Software glossary for accurate technical translations
- Auto-start Ollama and auto-pull models
- GPU-safe concurrency control via semaphore
