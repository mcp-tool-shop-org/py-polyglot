# Changelog

## 1.0.0 (2026-03-06)

- Initial release — Python port of polyglot-mcp
- 57 languages via TranslateGemma + Ollama
- Dual-use: Python library (`pip install py-polyglot`) + MCP server
- Core translation with chunking, batching, retry, and validation
- Markdown-aware translation preserving code blocks, tables, HTML
- Multi-language orchestrator with concurrent translation
- Segment-level caching with fuzzy matching (translation memory)
- Software glossary for accurate technical translations
- Auto-start Ollama and auto-pull models
- GPU-safe concurrency control via semaphore
