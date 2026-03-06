---
title: ハンドブック
description: polyglot-gpu の完全ガイド — Python 用のローカル GPU 翻訳。
sidebar:
  order: 0
---

polyglot-gpu ハンドブックへようこそ。これは、ローカル GPU 上で TranslateGemma を使用してテキストを翻訳するための完全なガイドです。

## 内容

- **[はじめに](/py-polyglot/handbook/getting-started/)** — インストール、設定、最初の翻訳を実行
- **[ライブラリの使用方法](/py-polyglot/handbook/usage/)** — テキスト、Markdown、多言語翻訳のための Python API
- **[MCP サーバー](/py-polyglot/handbook/mcp-server/)** — Claude Code やその他のクライアント向けの MCP サーバーとして実行
- **[設定](/py-polyglot/handbook/configuration/)** — モデル、環境変数、およびチューニング
- **[アーキテクチャ](/py-polyglot/handbook/architecture/)** — 12 のモジュールがどのように連携するか
- **[セキュリティ](/py-polyglot/handbook/security/)** — 脅威モデルとプライバシー保護

## polyglot-gpu について

polyglot-gpu は、[polyglot-mcp](https://github.com/mcp-tool-shop-org/polyglot-mcp) の Python 版です。Ollama を通じてローカルで実行される Google の TranslateGemma モデルを使用して、57 の言語にテキストを翻訳します。クラウドへの依存はなく、API キーも不要です。

ご自身のプロジェクトで **pip でインストール可能な Python ライブラリ** として、または Claude Code、Claude Desktop、およびその他の MCP クライアント向けの **MCP サーバー** として使用できます。

[トップページに戻る](/py-polyglot/)
