<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.md">English</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>Bibliothèque Python pour la traduction locale via GPU + serveur MCP — Traduction de Gemma via Ollama, 57 langues, sans dépendance cloud.</strong></p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/actions"><img src="https://github.com/mcp-tool-shop-org/py-polyglot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/v/polyglot-gpu" alt="PyPI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/pyversions/polyglot-gpu" alt="Python"></a>
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mcp-tool-shop-org/py-polyglot" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

Portage en Python de [polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp). Utilisez-le comme une **bibliothèque installable via pip** pour vos projets Python ou comme un **serveur MCP** pour Claude Code, Claude Desktop et d'autres clients MCP.

## Fonctionnalités

- **57 langues** — Traduction de Gemma via Ollama, fonctionnant entièrement localement sur votre GPU.
- **Aucune dépendance cloud** — pas de clés API, pas de connexion Internet requise après le téléchargement du modèle.
- **Double usage** — API de bibliothèque Python + serveur MCP dans un seul package.
- **Prise en charge du Markdown** — préserve les blocs de code, les tableaux, le HTML, les URL, les badges.
- **Mise en cache intelligente** — cache au niveau des segments avec correspondance floue (mémoire de traduction).
- **Glossaire logiciel** — 12 termes techniques intégrés pour des traductions précises.
- **Automatisation** — démarrage automatique d'Ollama, téléchargement automatique des modèles lors de la première utilisation.
- **Sûr pour le GPU** — la gestion de la concurrence par des sémaphores évite la surcharge de la VRAM.

## Prérequis

- Python >= 3.10
- [Ollama](https://ollama.com) installé localement
- GPU avec suffisamment de VRAM pour le modèle choisi :
- `translategemma:4b` — 3,3 Go (rapide, bonne qualité)
- `translategemma:12b` — 8,1 Go (équilibré, recommandé)
- `translategemma:27b` — 17 Go (lent, meilleure qualité)

## Installation

```bash
pip install polyglot-gpu
```

## Utilisation de la bibliothèque

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

## Utilisation du serveur MCP

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

Ou exécutez directement :

```bash
python -m pypolyglot
```

### Outils MCP

| Outil | Description |
|------|-------------|
| `translate_text` | Traduire du texte entre n'importe laquelle des 57 langues. |
| `translate_md` | Traduire le Markdown tout en préservant la structure. |
| `translate_all_langs` | Traduire dans plusieurs langues en même temps. |
| `list_languages` | Lister toutes les 57 langues prises en charge. |
| `check_status` | Vérifier la disponibilité d'Ollama et du modèle. |

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

## Variables d'environnement

| Variable | Valeur par défaut | Description |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | Modèle Ollama par défaut |
| `POLYGLOT_CONCURRENCY` | `1` | Nombre maximal d'appels Ollama simultanés |

## Sécurité

- Toutes les traductions s'effectuent localement — aucune donnée ne quitte votre machine.
- Pas de télémétrie, pas de clés API, pas de dépendance cloud.
- Consultez [SECURITY.md](SECURITY.md) pour le modèle de menace.

## Licence

MIT

---

Créé par <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
