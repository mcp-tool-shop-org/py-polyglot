<p align="center">
  <a href="README.md">English</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>ローカルGPU翻訳Pythonライブラリ + MCPサーバー — TranslateGemmaをOllama経由で利用。57言語に対応し、クラウドへの依存はありません。</strong></p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/actions"><img src="https://github.com/mcp-tool-shop-org/py-polyglot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/v/polyglot-gpu" alt="PyPI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/pyversions/polyglot-gpu" alt="Python"></a>
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mcp-tool-shop-org/py-polyglot" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

[polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp)のPython版。Pythonプロジェクトで**インストール可能なライブラリ**として、またはClaude Code、Claude Desktop、その他のMCPクライアント用の**MCPサーバー**として利用できます。

## 機能

- **57言語** — Ollama経由でTranslateGemmaを使用。100%ローカルでGPU上で動作
- **クラウドへの依存なし** — APIキーは不要、モデルのダウンロード後はインターネット接続も不要
- **多用途** — PythonライブラリAPI + MCPサーバーを1つのパッケージで提供
- **Markdown対応** — コードブロック、表、HTML、URL、バッジなどを保持
- **スマートキャッシュ** — セグメントレベルのキャッシュとファジーマッチング（翻訳メモリ）
- **ソフトウェア用語集** — 正確な翻訳のための12の組み込み技術用語
- **自動化** — Ollamaを自動起動、初回利用時にモデルを自動ダウンロード
- **GPU保護** — セマフォ制御による並行処理で、VRAMの過負荷を防止

## 必要条件

- Python >= 3.10
- ローカルに[Ollama](https://ollama.com)がインストールされていること
- 選択したモデルに必要なVRAMを搭載したGPU:
- `translategemma:4b` — 3.3 GB (高速、高品質)
- `translategemma:12b` — 8.1 GB (バランス、推奨)
- `translategemma:27b` — 17 GB (低速、最高品質)

## インストール

```bash
pip install polyglot-gpu
```

## ライブラリの使用方法

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

### オプション

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

## MCPサーバーの使用方法

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

または、直接実行:

```bash
python -m pypolyglot
```

### MCPツール

| ツール | 説明 |
|------|-------------|
| `translate_text` | 57の言語間でテキストを翻訳 |
| `translate_md` | 構造を保持しながらMarkdownを翻訳 |
| `translate_all_langs` | 複数の言語に同時に翻訳 |
| `list_languages` | サポートされている57の言語をすべて表示 |
| `check_status` | Ollamaとモデルの可用性を確認 |

## アーキテクチャ

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

## 環境変数

| 変数 | デフォルト値 | 説明 |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | デフォルトのOllamaモデル |
| `POLYGLOT_CONCURRENCY` | `1` | 最大同時Ollama呼び出し数 |

## セキュリティ

- すべての翻訳はローカルで実行 — データは一切外部に出ません
- テレメトリーなし、APIキー不要、クラウドへの依存なし
- 脅威モデルについては、[SECURITY.md](SECURITY.md)を参照してください。

## ライセンス

MIT

---

<a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>によって作成されました。
