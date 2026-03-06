# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Reporting a Vulnerability

Please report security issues to: 64996768+mcp-tool-shop@users.noreply.github.com

## Threat Model

- **Data touched:** Text sent to local Ollama API (`localhost:11434`), `.polyglot-cache.json` segment cache
- **Data NOT touched:** No files outside working directory, no browser data, OS credentials, or system files
- **Network:** HTTP to `localhost:11434` only — zero external/internet egress
- **No telemetry:** No data collection or transmission of any kind
- **No secrets:** No API keys, tokens, or credentials required or stored
