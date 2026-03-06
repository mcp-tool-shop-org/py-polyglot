# Ship Gate

> No repo is "done" until every applicable line is checked.
> Copy this into your repo root. Check items off per-release.

**Tags:** `[all]` every repo · `[npm]` `[pypi]` `[vsix]` `[desktop]` `[container]` published artifacts · `[mcp]` MCP servers · `[cli]` CLI tools

---

## A. Security Baseline

- [x] `[all]` SECURITY.md exists (report email, supported versions, response timeline) (2026-03-06)
- [x] `[all]` README includes threat model paragraph (data touched, data NOT touched, permissions required) (2026-03-06)
- [x] `[all]` No secrets, tokens, or credentials in source or diagnostics output (2026-03-06)
- [x] `[all]` No telemetry by default — state it explicitly even if obvious (2026-03-06)

### Default safety posture

- [ ] `[cli|mcp|desktop]` SKIP: no dangerous actions — translation only, no file delete/kill/restart
- [x] `[cli|mcp|desktop]` File operations constrained to known directories (2026-03-06) — cache writes to working dir only
- [x] `[mcp]` Network egress off by default (2026-03-06) — localhost:11434 only
- [x] `[mcp]` Stack traces never exposed — structured error results only (2026-03-06) — friendly_error() wraps all tool handlers

## B. Error Handling

- [x] `[all]` Errors follow the Structured Error Shape: `code`, `message`, `hint`, `cause?`, `retryable?` (2026-03-06)
- [ ] `[cli]` SKIP: not a CLI tool
- [ ] `[cli]` SKIP: not a CLI tool
- [x] `[mcp]` Tool errors return structured results — server never crashes on bad input (2026-03-06)
- [x] `[mcp]` State/config corruption degrades gracefully (stale data over crash) (2026-03-06) — cache handles corrupt JSON gracefully
- [ ] `[desktop]` SKIP: not a desktop app
- [ ] `[vscode]` SKIP: not a VS Code extension

## C. Operator Docs

- [x] `[all]` README is current: what it does, install, usage, supported platforms + runtime versions (2026-03-06)
- [x] `[all]` CHANGELOG.md (Keep a Changelog format) (2026-03-06)
- [x] `[all]` LICENSE file present and repo states support status (2026-03-06)
- [ ] `[cli]` SKIP: not a CLI tool
- [x] `[cli|mcp|desktop]` Logging levels defined: stderr output only, no secrets in output (2026-03-06)
- [x] `[mcp]` All tools documented with description + parameters (2026-03-06) — FastMCP auto-generates from docstrings
- [ ] `[complex]` SKIP: not complex — no background daemons or operational modes

## D. Shipping Hygiene

- [x] `[all]` `verify` script exists (test + build + smoke in one command) (2026-03-06) — Makefile: `make verify`
- [x] `[all]` Version in manifest matches git tag (2026-03-06)
- [x] `[all]` Dependency scanning runs in CI (ecosystem-appropriate) (2026-03-06) — pip-audit in CI
- [x] `[all]` Automated dependency update mechanism exists (2026-03-06) — dependabot monthly
- [ ] `[npm]` SKIP: not npm
- [x] `[pypi]` `python_requires` set (2026-03-06) — `>=3.10`
- [x] `[pypi]` Clean wheel + sdist build (2026-03-06) — verified locally
- [ ] `[vsix]` SKIP: not vsix
- [ ] `[desktop]` SKIP: not desktop

## E. Identity (soft gate — does not block ship)

- [x] `[all]` Logo in README header (2026-03-06)
- [x] `[all]` Translations (polyglot-mcp, 7 languages) (2026-03-06)
- [x] `[org]` Landing page (@mcptoolshop/site-theme) (2026-03-06)
- [x] `[all]` GitHub repo metadata: description, homepage, topics (2026-03-06)

---

## Gate Rules

**Hard gate (A–D):** Must pass before any version is tagged or published.
If a section doesn't apply, mark `SKIP:` with justification — don't leave it unchecked.

**Soft gate (E):** Should be done. Product ships without it, but isn't "whole."

**Checking off:**
```
- [x] `[all]` SECURITY.md exists (2026-02-27)
```

**Skipping:**
```
- [ ] `[pypi]` SKIP: not a Python project
```
