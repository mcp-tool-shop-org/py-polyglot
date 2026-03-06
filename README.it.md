<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.md">English</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>Libreria Python per la traduzione locale tramite GPU + server MCP — TranslateGemma tramite Ollama, 57 lingue, nessuna dipendenza dal cloud.</strong></p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/actions"><img src="https://github.com/mcp-tool-shop-org/py-polyglot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://codecov.io/gh/mcp-tool-shop-org/py-polyglot"><img src="https://codecov.io/gh/mcp-tool-shop-org/py-polyglot/branch/main/graph/badge.svg" alt="Codecov"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/v/polyglot-gpu" alt="PyPI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/pyversions/polyglot-gpu" alt="Python"></a>
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mcp-tool-shop-org/py-polyglot" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/handbook/"><img src="https://img.shields.io/badge/Handbook-docs-teal" alt="Handbook"></a>
</p>

---

Porting in Python di [polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp). Utilizzabile come **libreria installabile tramite pip** per i tuoi progetti Python oppure come **server MCP** per Claude Code, Claude Desktop e altri client MCP.

## Funzionalità

- **57 lingue** — Traduzione con TranslateGemma tramite Ollama, eseguita interamente localmente sulla tua GPU.
- **Nessuna dipendenza dal cloud** — nessuna chiave API, non è necessaria una connessione internet dopo il download del modello.
- **Doppio utilizzo** — API della libreria Python + server MCP in un unico pacchetto.
- **Supporto per Markdown** — preserva blocchi di codice, tabelle, HTML, URL, badge.
- **Caching intelligente** — cache a livello di segmento con corrispondenza approssimativa (memoria di traduzione).
- **Glossario software** — 12 termini tecnici integrati per traduzioni accurate.
- **Automatizzazione completa** — avvia automaticamente Ollama, scarica automaticamente i modelli al primo utilizzo.
- **Sicurezza per la GPU** — la gestione della concorrenza tramite semaforo previene il sovraccarico della VRAM.
- **Ottimizzato per la produzione** — gestione delle connessioni, logging strutturato, 100 test.

## Requisiti

- Python >= 3.10
- [Ollama](https://ollama.com) installato localmente
- GPU con VRAM sufficiente per il modello scelto:
- `translategemma:4b` — 3.3 GB (veloce, buona qualità)
- `translategemma:12b` — 8.1 GB (equilibrato, consigliato)
- `translategemma:27b` — 17 GB (lento, migliore qualità)

## Installazione

```bash
pip install polyglot-gpu
```

## Utilizzo della libreria

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

### Opzioni

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

## Utilizzo del server MCP

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

Oppure eseguilo direttamente:

```bash
python -m pypolyglot
```

### Strumenti MCP

| Strumento | Descrizione |
|------|-------------|
| `translate_text` | Traduci testo tra qualsiasi delle 57 lingue. |
| `translate_md` | Traduci il Markdown preservando la struttura. |
| `translate_all_langs` | Traduci in più lingue contemporaneamente. |
| `list_languages` | Elenca tutte le 57 lingue supportate. |
| `check_status` | Verifica la disponibilità di Ollama e del modello. |

## Architettura

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
│   ollama.py      │  httpx pooled client → Ollama
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

## Variabili d'ambiente

| Variabile | Valore predefinito | Descrizione |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | Modello Ollama predefinito |
| `POLYGLOT_CONCURRENCY` | `1` | Numero massimo di chiamate Ollama concorrenti |

## Sicurezza

- Tutte le traduzioni vengono eseguite localmente — nessun dato lascia il tuo computer.
- Nessuna telemetria, nessuna chiave API, nessuna dipendenza dal cloud.
- Consulta [SECURITY.md](SECURITY.md) per il modello di minaccia.

## Licenza

MIT

---

Creato da <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
