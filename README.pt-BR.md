<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.md">English</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>Biblioteca Python para tradução local em GPU + servidor MCP — TranslateGemma via Ollama, 57 idiomas, sem dependência de serviços em nuvem.</strong></p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/actions"><img src="https://github.com/mcp-tool-shop-org/py-polyglot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/py-polyglot/"><img src="https://img.shields.io/pypi/v/py-polyglot" alt="PyPI"></a>
  <a href="https://pypi.org/project/py-polyglot/"><img src="https://img.shields.io/pypi/pyversions/py-polyglot" alt="Python"></a>
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mcp-tool-shop-org/py-polyglot" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

Port para Python de [polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp). Use como uma **biblioteca instalável via pip** para seus projetos Python ou como um **servidor MCP** para Claude Code, Claude Desktop e outros clientes MCP.

## Características

- **57 idiomas** — Tradução com o TranslateGemma via Ollama, executando 100% localmente na sua GPU.
- **Sem dependência de serviços em nuvem** — sem chaves de API, sem necessidade de internet após o download do modelo.
- **Uso duplo** — API de biblioteca Python + servidor MCP em um único pacote.
- **Compatível com Markdown** — preserva blocos de código, tabelas, HTML, URLs, badges.
- **Cache inteligente** — cache por segmento com correspondência aproximada (memória de tradução).
- **Glossário de termos técnicos** — 12 termos técnicos integrados para traduções precisas.
- **Automatização completa** — inicia automaticamente o Ollama, baixa automaticamente os modelos na primeira utilização.
- **Seguro para GPU** — a concorrência controlada por semáforo evita a sobrecarga de VRAM.

## Requisitos

- Python >= 3.10
- [Ollama](https://ollama.com) instalado localmente
- GPU com VRAM suficiente para o modelo escolhido:
- `translategemma:4b` — 3,3 GB (rápido, boa qualidade)
- `translategemma:12b` — 8,1 GB (equilibrado, recomendado)
- `translategemma:27b` — 17 GB (lento, melhor qualidade)

## Instalação

```bash
pip install py-polyglot
```

## Uso da Biblioteca

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

### Opções

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

## Uso do Servidor MCP

### Claude Code

```json
{
  "mcpServers": {
    "py-polyglot": {
      "command": "py-polyglot"
    }
  }
}
```

Ou execute diretamente:

```bash
python -m pypolyglot
```

### Ferramentas MCP

| Ferramenta | Descrição |
|------|-------------|
| `translate_text` | Traduz texto entre qualquer um dos 57 idiomas. |
| `translate_md` | Traduz Markdown, preservando a estrutura. |
| `translate_all_langs` | Traduz para vários idiomas simultaneamente. |
| `list_languages` | Lista todos os 57 idiomas suportados. |
| `check_status` | Verifica a disponibilidade do Ollama e do modelo. |

## Arquitetura

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

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | Modelo Ollama padrão |
| `POLYGLOT_CONCURRENCY` | `1` | Número máximo de chamadas Ollama simultâneas |

## Segurança

- Todas as traduções são executadas localmente — nenhum dado sai da sua máquina.
- Sem telemetria, sem chaves de API, sem dependência de serviços em nuvem.
- Consulte [SECURITY.md](SECURITY.md) para o modelo de ameaças.

## Licença

MIT

---

Desenvolvido por <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
