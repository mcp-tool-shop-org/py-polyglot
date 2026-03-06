---
title: 手册
description: polyglot-gpu 的完整指南——用于 Python 的本地 GPU 翻译。
sidebar:
  order: 0
---

欢迎来到 polyglot-gpu 手册。这是一份关于如何在本地 GPU 上使用 TranslateGemma 进行文本翻译的完整指南。

## 内容概要

- **[入门](/py-polyglot/handbook/getting-started/)** — 安装、配置并运行您的第一个翻译
- **[库的使用](/py-polyglot/handbook/usage/)** — 用于文本、Markdown 和多语言翻译的 Python API
- **[MCP 服务器](/py-polyglot/handbook/mcp-server/)** — 作为 MCP 服务器运行，用于 Claude Code 和其他客户端
- **[配置](/py-polyglot/handbook/configuration/)** — 模型、环境变量和调优
- **[架构](/py-polyglot/handbook/architecture/)** — 12 个模块如何协同工作
- **[安全性](/py-polyglot/handbook/security/)** — 威胁模型和隐私保障

## 关于 polyglot-gpu

polyglot-gpu 是 [polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp) 的 Python 移植版本。它使用 Google 的 TranslateGemma 模型，通过 Ollama 在本地进行翻译，支持 57 种语言。无需任何云依赖，无需 API 密钥。

您可以在自己的项目中将其用作一个 **可安装的 Python 库**，也可以将其用作 Claude Code、Claude Desktop 和其他 MCP 客户端的 **MCP 服务器**。

[返回主页](/py-polyglot/)
