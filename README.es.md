<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.md">English</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>Biblioteca de traducción local para GPU en Python + servidor MCP — TraduceGemma a través de Ollama, 57 idiomas, sin dependencia de la nube.</strong></p>

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

Port de Python de [polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp). Úsalo como una **biblioteca instalable con pip** para tus proyectos de Python o como un **servidor MCP** para Claude Code, Claude Desktop y otros clientes MCP.

## Características

- **57 idiomas** — TraduceGemma a través de Ollama, ejecutándose completamente localmente en tu GPU.
- **Sin dependencia de la nube** — no requiere claves de API, ni conexión a internet después de la descarga del modelo.
- **Uso dual** — API de biblioteca de Python + servidor MCP en un solo paquete.
- **Compatible con Markdown** — conserva bloques de código, tablas, HTML, URLs, insignias.
- **Caché inteligente** — caché a nivel de segmento con coincidencia difusa (memoria de traducción).
- **Glosario de software** — 12 términos técnicos integrados para traducciones precisas.
- **Automatización total** — inicia automáticamente Ollama, descarga automáticamente los modelos en la primera ejecución.
- **Seguro para GPU** — la concurrencia controlada por semáforo evita la sobrecarga de VRAM.
- **Optimizado para producción** — agrupación de conexiones, registro estructurado, 100 pruebas.

## Requisitos

- Python >= 3.10
- [Ollama](https://ollama.com) instalado localmente
- GPU con suficiente VRAM para el modelo elegido:
- `translategemma:4b` — 3.3 GB (rápido, buena calidad)
- `translategemma:12b` — 8.1 GB (equilibrado, recomendado)
- `translategemma:27b` — 17 GB (lento, mejor calidad)

## Instalación

```bash
pip install polyglot-gpu
```

## Uso de la biblioteca

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

### Opciones

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

## Uso del servidor MCP

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

O ejecútalo directamente:

```bash
python -m pypolyglot
```

### Herramientas MCP

| Herramienta | Descripción |
|------|-------------|
| `translate_text` | Traduce texto entre cualquiera de los 57 idiomas. |
| `translate_md` | Traduce Markdown conservando la estructura. |
| `translate_all_langs` | Traduce a múltiples idiomas a la vez. |
| `list_languages` | Lista todos los 57 idiomas soportados. |
| `check_status` | Verifica la disponibilidad de Ollama y el modelo. |

## Arquitectura

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

## Variables de entorno

| Variable | Valor predeterminado | Descripción |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | Modelo Ollama predeterminado |
| `POLYGLOT_CONCURRENCY` | `1` | Número máximo de llamadas concurrentes a Ollama |

## Seguridad

- Todas las traducciones se realizan localmente — ningún dato sale de tu máquina.
- Sin telemetría, sin claves de API, sin dependencia de la nube.
- Consulta [SECURITY.md](SECURITY.md) para obtener información sobre el modelo de amenazas.

## Licencia

MIT

---

Creado por <a href="https://mcp-tool-shop.github.io/">MCP Tool Shop</a>
