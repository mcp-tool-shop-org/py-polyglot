<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.md">English</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>本地 GPU 翻译 Python 库 + MCP 服务器 — 通过 Ollama 实现 TranslateGemma，支持 57 种语言，无需任何云端依赖。</strong></p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/actions"><img src="https://github.com/mcp-tool-shop-org/py-polyglot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/v/polyglot-gpu" alt="PyPI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/pyversions/polyglot-gpu" alt="Python"></a>
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mcp-tool-shop-org/py-polyglot" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

这是 [polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp) 的 Python 移植版本。您可以将其用作 Python 项目的 **可安装的库**，也可以用作 Claude Code、Claude Desktop 以及其他 MCP 客户端的 **MCP 服务器**。

## 特性

- **57 种语言** — 通过 Ollama 实现 TranslateGemma，完全在您的 GPU 本地运行。
- **零云端依赖** — 无需 API 密钥，模型下载后无需连接互联网。
- **双重用途** — Python 库 API + MCP 服务器，集成在一个软件包中。
- **支持 Markdown** — 保留代码块、表格、HTML、URL 和徽章。
- **智能缓存** — 基于分段的缓存，采用模糊匹配（翻译记忆）。
- **软件术语表** — 内置 12 个技术术语，用于准确的翻译。
- **自动配置** — 自动启动 Ollama，首次使用时自动下载模型。
- **GPU 保护** — 信号量控制的并发，防止 VRAM 过载。

## 系统要求

- Python >= 3.10
- 本地安装 [Ollama](https://ollama.com)
- 具有足够 VRAM 的 GPU，用于您选择的模型：
- `translategemma:4b` — 3.3 GB (速度快，质量好)
- `translategemma:12b` — 8.1 GB (平衡，推荐)
- `translategemma:27b` — 17 GB (速度慢，质量最佳)

## 安装

```bash
pip install polyglot-gpu
```

## 库的使用方法

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

### 选项

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

## MCP 服务器的使用方法

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

或者直接运行：

```bash
python -m pypolyglot
```

### MCP 工具

| 工具 | 描述 |
|------|-------------|
| `translate_text` | 在 57 种语言之间进行文本翻译。 |
| `translate_md` | 在保留结构的同时翻译 Markdown。 |
| `translate_all_langs` | 一次性翻译成多种语言。 |
| `list_languages` | 列出所有 57 种支持的语言。 |
| `check_status` | 检查 Ollama 和模型是否可用。 |

## 架构

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

## 环境变量

| 变量 | 默认值 | 描述 |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | 默认 Ollama 模型 |
| `POLYGLOT_CONCURRENCY` | `1` | 最大并发 Ollama 调用次数 |

## 安全性

- 所有翻译都在本地运行 — 您的数据不会离开您的机器。
- 没有遥测数据，无需 API 密钥，无需云端依赖。
- 详情请参阅 [SECURITY.md](SECURITY.md)，了解安全模型。

## 许可证

MIT

---

由 <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a> 构建。
