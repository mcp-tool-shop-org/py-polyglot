import type { SiteConfig } from '@mcptoolshop/site-theme';

export const config: SiteConfig = {
  title: 'polyglot-gpu',
  description: 'Local GPU translation Python library + MCP server — TranslateGemma via Ollama, 57 languages, zero cloud dependency.',
  logoBadge: 'Py',
  brandName: 'polyglot-gpu',
  repoUrl: 'https://github.com/mcp-tool-shop-org/py-polyglot',
  pypiUrl: 'https://pypi.org/project/polyglot-gpu/',
  footerText: 'MIT Licensed — built by <a href="https://mcp-tool-shop.github.io/" style="color:var(--color-muted);text-decoration:underline">MCP Tool Shop</a>',

  hero: {
    badge: 'Open source',
    headline: 'polyglot-gpu',
    headlineAccent: '57 languages on your GPU.',
    description: 'Python translation library + MCP server. TranslateGemma via Ollama — zero cloud dependency, zero API keys.',
    primaryCta: { href: '#usage', label: 'Get started' },
    secondaryCta: { href: 'handbook/', label: 'Read the Handbook' },
    previews: [
      { label: 'Install', code: 'pip install polyglot-gpu' },
      { label: 'Translate', code: 'result = await translate("Hello", "en", "ja")' },
      { label: 'MCP', code: 'python -m pypolyglot' },
    ],
  },

  sections: [
    {
      kind: 'features',
      id: 'features',
      title: 'Features',
      subtitle: 'Everything runs locally on your GPU.',
      features: [
        { title: '57 Languages', desc: 'TranslateGemma supports 57 languages including CJK, Arabic, Hindi, and all major European languages.' },
        { title: 'Dual-Use', desc: 'Use as a pip-installable Python library or as an MCP server for Claude Code, Claude Desktop, and other clients.' },
        { title: 'Markdown-Aware', desc: 'Translates prose while preserving code blocks, tables, HTML, URLs, and badges intact.' },
        { title: 'Smart Cache', desc: 'Segment-level cache with Levenshtein fuzzy matching — translation memory that speeds up repeat translations.' },
        { title: 'Auto-Everything', desc: 'Auto-starts Ollama, auto-pulls TranslateGemma models. Zero manual setup on first run.' },
        { title: 'GPU-Safe', desc: 'Semaphore-controlled concurrency prevents VRAM overload. Works on 4 GB to 24 GB GPUs.' },
      ],
    },
    {
      kind: 'code-cards',
      id: 'usage',
      title: 'Usage',
      cards: [
        { title: 'Install', code: 'pip install polyglot-gpu' },
        { title: 'Simple translation', code: "from pypolyglot import translate\n\nresult = await translate(\"Hello world\", \"en\", \"ja\")\nprint(result.translation)  # こんにちは世界" },
        { title: 'Markdown translation', code: "from pypolyglot import translate_markdown\n\nresult = await translate_markdown(md, \"en\", \"fr\")\nprint(result.markdown)" },
        { title: 'MCP server', code: "# Add to Claude Code config:\n{\n  \"mcpServers\": {\n    \"polyglot-gpu\": {\n      \"command\": \"polyglot-gpu\"\n    }\n  }\n}" },
      ],
    },
    {
      kind: 'data-table',
      id: 'models',
      title: 'Models',
      subtitle: 'Choose based on your GPU VRAM.',
      columns: ['Model', 'VRAM', 'Speed', 'Quality'],
      rows: [
        ['translategemma:4b', '3.3 GB', 'Fast', 'Good'],
        ['translategemma:12b', '8.1 GB', 'Balanced', 'Recommended'],
        ['translategemma:27b', '17 GB', 'Slow', 'Best'],
      ],
    },
    {
      kind: 'api',
      id: 'mcp-tools',
      title: 'MCP Tools',
      apis: [
        { signature: 'translate_text(text, from_lang, to_lang, model?, glossary?)', description: 'Translate text between any of 57 supported languages.' },
        { signature: 'translate_md(markdown, from_lang, to_lang, model?)', description: 'Translate markdown while preserving code blocks, tables, and HTML.' },
        { signature: 'translate_all_langs(markdown, from_lang?, languages?, model?, concurrency?)', description: 'Translate into multiple languages at once (default: 7 languages).' },
        { signature: 'list_languages()', description: 'List all 57 supported languages with codes.' },
        { signature: 'check_status()', description: 'Check Ollama availability and installed TranslateGemma models.' },
      ],
    },
  ],
};
