# Installation Guide

This guide covers installing and configuring the **SRE Extension** across different terminal harnesses (Google Gemini CLI, Antigravity CLI, and Claude Code).

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

*   **Workspace-Level**: Place or symlink this repository folder inside `.claude/plugins/sre-extension/` at the root of your workspace.
*   **Global-Level**: Run Claude Code with the plugin directory flag:
```bash
claude --plugin-dir "/path/to/sre-extension"
```

### 4. OpenAI Codex Setup

*   **Workspace-Level / Manual Integration**: Place or symlink this repository folder inside `.codex-plugin/` or your configured plugin marketplace/custom project directory.
