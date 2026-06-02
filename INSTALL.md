# Installation Guide

This guide covers installing and configuring the **SRE Extension** across different terminal harnesses (Google Gemini CLI, Antigravity CLI, and Claude Code).

---

## 📺 Installation & Setup Walkthrough

Watch the step-by-step video guide to get up and running with the SRE Extension:

[![SRE Extension Installation & Setup Walkthrough](https://img.youtube.com/vi/_sqPO2oYUoM/maxresdefault.jpg)](https://youtu.be/_sqPO2oYUoM)

---

## Prerequisites

Ensure you have **at least one** of the supported CLI harnesses installed:
*   [Gemini CLI](https://geminicli.com/) (*being deprecated soon*)
*   [Antigravity CLI (agy)](https://antigravity.google/)
*   [Claude Code](https://github.com/anthropics/claude-code)

---

## 🚀 Easy Installation via Justfile

If you have `just` installed, we provide a unified set of recipes to install the extension for your chosen harness:

```bash
# Google Antigravity CLI (agy)
just install-agy

# Google Gemini CLI (deprecated)
just install-geminicli

# Claude Code
just install-claude
```

---

## 🛠️ Manual Installation Methods

If you prefer not to use `just`, you can install the extension manually.

### 1. Google Gemini CLI (deprecated)

You can install this extension via the Gemini CLI's install command:
```bash
gemini extensions install https://github.com/gemini-cli-extensions/sre
```

This will allow you to easily manage its lifecycle by easily updating the extension with `/extensions update --all`.

### 2. Antigravity Setup

*   **Workspace-Level**: Place or symlink this repository folder inside `.agents/plugins/sre-extension/` or `_agents/plugins/sre-extension/` at the root of your workspace.
*   **Global-Level**: Place or symlink this repository folder inside `~/.gemini/config/plugins/sre-extension/`.

To install globally manually:
```bash
mkdir -p ~/.gemini/config/plugins/
git clone git@github.com:gemini-cli-extensions/sre.git ~/.gemini/config/plugins/sre-extension
```

### 3. Claude Code Setup

Claude Code has **two distinct ways** to load this extension. They behave very
differently, so pick the one that matches your needs.

#### Option A — Session-scoped (`--plugin-dir`)

Loads the plugin for a **single Claude session only**. Nothing is written to your
config; when you quit Claude, it is gone. Great for trying it out or for
development on the extension itself.

```bash
claude --plugin-dir "/path/to/sre-extension"
# or, from inside this repo:
just install-claude
```

#### Option B — Persistent install (marketplace)

Installs the extension **permanently** so its skills are available in every
future Claude session (including non-interactive `claude -p "..."` runs). This
repo doubles as a single-plugin **marketplace** (see `.claude-plugin/marketplace.json`),
so the flow is "add the marketplace, then install the plugin from it":

```bash
claude plugin marketplace add gemini-cli-extensions/sre
claude plugin install sre-extension@sre
# or, from inside this repo:
just install-claude-persistent
```

Here the marketplace is named **`sre`** and the plugin is named
**`sre-extension`**, which is why the install reference is `sre-extension@sre`.

**Install scope** (`--scope`) controls *where* the install is recorded:

| Scope | Flag | Stored in | Loads in `claude -p`? |
| --- | --- | --- | --- |
| User (default) | `--scope user` | `~/.claude` (global) | ✅ Yes |
| Project | `--scope project` | `.claude/settings.json` (shared, committed) | ✅ Yes |
| Local | `--scope local` | `.claude/settings.local.json` (per-machine) | ⚠️ Did **not** surface skills in `-p` testing — prefer `user` or `project` |

Useful management commands:

```bash
claude plugin list                       # show installed plugins + scope + status
claude plugin details sre-extension      # component inventory + token cost
claude plugin uninstall sre-extension    # remove it (add --scope to match install)
claude plugin marketplace remove sre     # forget the marketplace
claude plugin validate .                 # validate the plugin/marketplace manifests
```

> **Note on `.claude/plugins/`:** unlike Gemini/Antigravity, Claude Code does
> **not** auto-discover plugins dropped into a `.claude/plugins/` folder. Use one
> of the two options above instead.

### 4. OpenAI Codex Setup

*   **Workspace-Level / Manual Integration**: Place or symlink this repository folder inside `.codex-plugin/` or your configured plugin marketplace/custom project directory.
