# Installation Guide

This guide covers installing and configuring the **SRE Extension** across different terminal harnesses (Google Gemini CLI, Antigravity CLI, and Claude Code).

## Prerequisites

Ensure you have one of the supported CLI harnesses installed:
*   [Gemini CLI](https://geminicli.com/)
*   [Antigravity CLI (agy)](https://antigravity.google/)
*   [Claude Code](https://github.com/anthropics/claude-code)

---

## 🚀 Easy Installation via Justfile

If you have `just` installed, we provide a unified set of recipes to install the extension for your chosen harness. Run `just -l` to see available recipes, or run the command for your preferred CLI:

### 1. Google Antigravity CLI (`agy`)
To install the extension into the Antigravity CLI's plugin directory:
```bash
just install-agy
```

### 2. Google Gemini CLI
To install the extension using the standard Gemini CLI extensions mechanism:
```bash
just install-geminicli
```

### 3. Claude Code
To launch Claude Code with this extension loaded globally as a plugin:
```bash
just install-claude
```

---

## 🛠️ Manual Installation Methods

If you prefer not to use `just`, you can install the extension manually.

### Gemini CLI (Recommended)
You can install this extension via the Gemini CLI's install command:
```bash
gemini extensions install https://github.com/gemini-cli-extensions/sre
```

### Antigravity CLI (`agy`)
You can clone this repository directly into the `agy` plugins directory:
```bash
mkdir -p ~/.gemini/config/plugins
git clone git@github.com:gemini-cli-extensions/sre.git ~/.gemini/config/plugins/sre-extension
```

### Claude Code
Run Claude Code with the `--plugin-dir` flag pointing to this repository's absolute path:
```bash
claude --plugin-dir "/path/to/sre-extension"
```
