<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.md">English</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/polyglot-mcp/readme.png" alt="py-polyglot" width="400">
</p>

<p align="center"><strong>स्थानीय जीपीयू अनुवाद पाइथन लाइब्रेरी + एमसीपी सर्वर — ट्रांसलेटगेमा वाया ओललामा, 57 भाषाएँ, शून्य क्लाउड निर्भरता।</strong></p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/actions"><img src="https://github.com/mcp-tool-shop-org/py-polyglot/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/v/polyglot-gpu" alt="PyPI"></a>
  <a href="https://pypi.org/project/polyglot-gpu/"><img src="https://img.shields.io/pypi/pyversions/polyglot-gpu" alt="Python"></a>
  <a href="https://github.com/mcp-tool-shop-org/py-polyglot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/mcp-tool-shop-org/py-polyglot" alt="License"></a>
  <a href="https://mcp-tool-shop-org.github.io/py-polyglot/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

[polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp) का पाइथन संस्करण। इसे अपने पाइथन प्रोजेक्ट्स के लिए एक **पिप-इंस्टॉल करने योग्य लाइब्रेरी** के रूप में या क्लाउड कोड, क्लाउड डेस्कटॉप और अन्य एमसीपी क्लाइंट के लिए एक **एमसीपी सर्वर** के रूप में उपयोग करें।

## विशेषताएं

- **57 भाषाएँ** — ट्रांसलेटगेमा वाया ओललामा, जो आपके जीपीयू पर 100% स्थानीय रूप से चलता है।
- **शून्य क्लाउड निर्भरता** — किसी एपीआई कुंजी की आवश्यकता नहीं, मॉडल डाउनलोड करने के बाद इंटरनेट की आवश्यकता नहीं।
- **दोहरे उपयोग** — पाइथन लाइब्रेरी एपीआई + एक पैकेज में एमसीपी सर्वर।
- **मार्कडाउन-जागरूक** — कोड ब्लॉक, टेबल, एचटीएमएल, यूआरएल, बैज संरक्षित करता है।
- **स्मार्ट कैशिंग** — सेगमेंट-स्तरीय कैशिंग, जिसमें अस्पष्ट मिलान (अनुवाद मेमोरी) शामिल है।
- **सॉफ्टवेयर शब्दावली** — सटीक अनुवादों के लिए 12 अंतर्निहित तकनीकी शब्द।
- **ऑटो-सब कुछ** — ओललामा को स्वचालित रूप से शुरू करता है, पहली बार उपयोग करने पर स्वचालित रूप से मॉडल डाउनलोड करता है।
- **जीपीयू-सुरक्षित** — सिमाफोर-नियंत्रित समवर्तीता, जो वीआरएएम ओवरलोड को रोकता है।

## आवश्यकताएं

- पाइथन >= 3.10
- स्थानीय रूप से [ओलामा](https://ollama.com) स्थापित
- आपके द्वारा चुने गए मॉडल के लिए पर्याप्त वीआरएएम वाला जीपीयू:
- `translategemma:4b` — 3.3 जीबी (तेज़, अच्छी गुणवत्ता)
- `translategemma:12b` — 8.1 जीबी (संतुलित, अनुशंसित)
- `translategemma:27b` — 17 जीबी (धीमा, सर्वोत्तम गुणवत्ता)

## इंस्टॉल करें

```bash
pip install polyglot-gpu
```

## लाइब्रेरी का उपयोग

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

### विकल्प

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

## एमसीपी सर्वर का उपयोग

### क्लाउड कोड

```json
{
  "mcpServers": {
    "polyglot-gpu": {
      "command": "polyglot-gpu"
    }
  }
}
```

या सीधे चलाएं:

```bash
python -m pypolyglot
```

### एमसीपी उपकरण

| उपकरण | विवरण |
|------|-------------|
| `translate_text` | 57 में से किसी भी भाषा के बीच टेक्स्ट का अनुवाद करें। |
| `translate_md` | संरचना को संरक्षित करते हुए मार्कडाउन का अनुवाद करें। |
| `translate_all_langs` | एक साथ कई भाषाओं में अनुवाद करें। |
| `list_languages` | सभी 57 समर्थित भाषाओं की सूची देखें। |
| `check_status` | ओलामा + मॉडल की उपलब्धता की जांच करें। |

## आर्किटेक्चर

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

## पर्यावरण चर

| चर | डिफ़ॉल्ट | विवरण |
|----------|---------|-------------|
| `POLYGLOT_MODEL` | `translategemma:12b` | डिफ़ॉल्ट ओललामा मॉडल |
| `POLYGLOT_CONCURRENCY` | `1` | अधिकतम समवर्ती ओललामा कॉल |

## सुरक्षा

- सभी अनुवाद स्थानीय रूप से किए जाते हैं — कोई भी डेटा आपके मशीन से बाहर नहीं जाता है।
- कोई टेलीमेट्री नहीं, कोई एपीआई कुंजी नहीं, कोई क्लाउड निर्भरता नहीं।
- खतरे के मॉडल के लिए [सुरक्षा.एमडी](सुरक्षा.एमडी) देखें।

## लाइसेंस

एमआईटी

---

<a href="https://mcp-tool-shop.github.io/">एमसीपी टूल शॉप</a> द्वारा निर्मित।
