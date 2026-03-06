<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>Local GPU translation Python library + MCP server — TranslateGemma via Ollama, 57 languages, zero cloud dependency.</strong></p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/actions"><img src="https://github.com/mcp-tool-shop-org/py-polyglot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://codecov.io/gh/mcp-tool-shop-org/py-polyglot"><img src="https://codecov.io/gh/mcp-tool-shop-org/py-polyglot/branch/main/graph/badge.svg" alt="Codecov"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/v/polyglot-gpu" alt="PyPI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/pyversions/polyglot-gpu" alt="Python"></a>
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mcp-tool-shop-org/py-polyglot" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

Python port of [polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp). Use as a **pip-installable library** for your Python projects or as an **MCP server** for Claude Code, Claude Desktop, and other MCP clients.

## Features

- **57 languages** — TranslateGemma via Ollama, running 100% locally on your GPU
- **Zero cloud dependency** — no API keys, no internet required after model download
- **Dual-use** — Python library API + MCP server in one package
- **Markdown-aware** — preserves code blocks, tables, HTML, URLs, badges
- **Smart caching** — segment-level cache with fuzzy matching (translation memory)
- **Software glossary** — 12 built-in tech terms for accurate translations
- **Auto-everything** — auto-starts Ollama, auto-pulls models on first use
- **GPU-safe** — semaphore-controlled concurrency prevents VRAM overload

## Requirements

- Python >= 3.10
- [Ollama](https://ollama.com) installed locally
- GPU with sufficient VRAM for your chosen model:
  - `translategemma:4b` — 3.3 GB (fast, good quality)
  - `translategemma:12b` — 8.1 GB (balanced, recommended)
  - `translategemma:27b` — 17 GB (slow, best quality)

## Install

```bash
pip install polyglot-gpu
```

## Library Usage

```python
import asyncio
from pypolyglot import translate, translate_markdown, translate_all

async def main():
    # Simple translation
    result = await translate("Hello world", "en", "ja")
    print(result.translation)  # こんにちは世界

    # Markdown translation (preserves structure)
    md = "## Features\n\nLocal GPU translation with **zero cloud dependency**."
    result = await translate_markdown(md, "en", "fr")
    print(result.markdown)

    # Multi-language (7 languages at once)
    result = await translate_all(md, source_lang="en")
    for r in result.results:
        print(f"{r.name}: {r.status}")

asyncio.run(main())
```

### Options

```python
from pypolyglot import translate, TranslateOptions, GlossaryEntry

# Custom model
result = await translate("Hello", "en", "ja",
    TranslateOptions(model="translategemma:4b"))

# Custom glossary
result = await translate("Deploy the Widget", "en", "ja",
    TranslateOptions(glossary=[
        GlossaryEntry("Widget", {"ja": "ウィジェット"})
    ]))

# Streaming
result = await translate("Hello world", "en", "ja",
    TranslateOptions(on_token=lambda t: print(t, end="")))
```

## MCP Server Usage

### Claude Code

```json
{
  "mcpServers": {
    "polyglot-gpu": {
      "command": "polyglot-gpu"
    }
  }
}
```

Or run directly:

```bash
python -m pypolyglot
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `translate_text` | Translate text between any of 57 languages |
| `translate_md` | Translate markdown while preserving structure |
| `translate_all_langs` | Translate into multiple languages at once |
| `list_languages` | List all 57 supported languages |
| `check_status` | Check Ollama + model availability |

## Architecture

```
MCP Client (Claude Code, etc.)
      │ MCP protocol (stdio)
      ▼
┌──────────────────┐
│   server.py      │  5 MCP tools (FastMCP)
├──────────────────┤
│  translate.py    │  Chunking, batching, streaming
│  markdown.py     │  Markdown segmentation
│  translate_all   │  Multi-language orchestrator
│  semaphore.py    │  GPU-safe concurrency
│  validate.py     │  Output validation
├──────────────────┤
│   ollama.py      │  httpx client → localhost:11434
│   cache.py       │  Segment cache + fuzzy memory
│  glossary.py     │  Software term dictionary
│ languages.py     │  57 language definitions
│   polish.py      │  Post-translation cleanup
│   errors.py      │  Structured error class
└──────────────────┘
      │ HTTP (httpx)
      ▼
   Ollama + TranslateGemma (GPU)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | Default Ollama model |
| `POLYGLOT_CONCURRENCY` | `1` | Max concurrent Ollama calls |

## Security

- All translation runs locally — zero data leaves your machine
- No telemetry, no API keys, no cloud dependency
- See [SECURITY.md](SECURITY.md) for threat model

## License

MIT

---

Built by <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
