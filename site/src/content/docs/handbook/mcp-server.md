---
title: MCP Server
description: Run polyglot-gpu as an MCP server for Claude Code and other clients.
sidebar:
  order: 3
---

polyglot-gpu includes a built-in MCP (Model Context Protocol) server powered by FastMCP. This lets Claude Code, Claude Desktop, and other MCP clients translate text directly.

## Setup for Claude Code

Add to your MCP config:

```json
{
  "mcpServers": {
    "polyglot-gpu": {
      "command": "polyglot-gpu"
    }
  }
}
```

Or run the server directly:

```bash
python -m pypolyglot
```

The server uses stdio transport by default.

## Available tools

| Tool | Description |
|------|-------------|
| `translate_text` | Translate text between any of 57 languages |
| `translate_md` | Translate markdown while preserving structure |
| `translate_all_langs` | Translate into multiple languages at once |
| `list_languages` | List all 57 supported languages with codes |
| `check_status` | Check Ollama availability and installed models |

## translate_text

Translates plain text between two languages.

**Parameters:**
- `text` (string, required) — Text to translate
- `from_lang` (string, required) — Source language code (e.g., "en")
- `to_lang` (string, required) — Target language code (e.g., "ja")
- `model` (string, optional) — Ollama model override
- `glossary` (array, optional) — Custom glossary entries

## translate_md

Translates markdown content while preserving code blocks, tables, HTML, and structure.

**Parameters:**
- `markdown` (string, required) — Markdown content to translate
- `from_lang` (string, required) — Source language code
- `to_lang` (string, required) — Target language code
- `model` (string, optional) — Ollama model override

## translate_all_langs

Translates markdown into multiple languages concurrently. Injects language nav bars into each translation.

**Parameters:**
- `markdown` (string, required) — Markdown content
- `from_lang` (string, optional, default: "en") — Source language
- `languages` (array, optional) — Target language codes (default: 7 languages)
- `model` (string, optional) — Ollama model override
- `concurrency` (number, optional, default: 2) — Max concurrent translations (1-3)

## list_languages

Returns all 57 supported language codes and names. No parameters.

## check_status

Reports Ollama availability, installed TranslateGemma models, and GPU readiness. No parameters.
