# Changelog - OneMCP Setup Skill

All notable changes to this skill will be documented in this file.

## [0.0.10] - 2026-07-03
### Added
- **GitHub Copilot CLI support**: `setup_onemcp.py` now accepts `--harness {gemini,antigravity,copilot}` and writes the correct MCP config format and path per harness (`~/.copilot/mcp-config.json` using Copilot's `type/url/tools` wire format).
- **Centralized harness registry**: `harness_registry.py` as the single source of truth for all harness configuration (config file paths, MCP entry builders, CLI commands). Both `setup_onemcp.py` and `verify_setup.py` import from it.
- **Typed harness config**: `harness_registry.py` exposes `HarnessName(str, Enum)`, `HarnessCommand(str, Enum)`, and a `HarnessConfig` frozen dataclass with a `.paths(scope)` method.
- **Harness-agnostic MCP verification**: `verify_setup.py` now accepts `--harness {gemini,antigravity,copilot}` and dispatches to the correct CLI command via `HarnessCommand.MCP_LIST`. Config file paths are derived from the registry.

## [0.0.9] - 2026-05-28
### Added
- **Antigravity CLI Support**: Added automated configuration support for the modern `agy` CLI and Antigravity Editor.
- **Tailored Config Outputs**: The setup script now creates clean, tailored configurations (using strictly legacy `httpUrl` inside `.gemini/settings.json`, and strictly modern `serverUrl` inside `mcp_config.json` files) to avoid key pollution and comply with each tool's specification.
- **Reference Templates**: Created structured sample templates under `references/gemini/settings.json` and `references/antigravity/mcp_config.json`.
- **Diagnostic Verification**: Updated `verify_setup.py` to seamlessly check configuration health across both old and new paths.

### Author
- Riccardo

## [0.0.4] - 2026-03-30
### Added
- **New OneMCP Endpoints**: Added automated support for GKE (`container.googleapis.com`) and Cloud Monitoring (`monitoring.googleapis.com`) MCP servers.
- **Diagnostic Tool**: Created `test_mcp_endpoint.sh`, a curl-based script to directly query and list tools for any OneMCP endpoint without requiring the Gemini CLI.

### Changed
- Updated `verify_setup.py` and `SKILL.md` to reflect the expanded set of managed servers.

### Author
- Riccardo

## [0.0.3] - 2026-03-30
### Added
- **Actionable Fix**: Enhanced `verify_setup.py` to propose an account-specific synchronization command (`gcloud auth application-default login --account=...`).

### Changed
- Refined `SKILL.md` to reflect the updated fix command.

### Author
- Riccardo

## [0.0.2] - 2026-03-30
### Added
- **Security Check:** New automated identity consistency check in `verify_setup.py`. This ensures the `gcloud` identity matches the Application Default Credentials (ADC) identity used by MCP servers.
- **Identity Mismatch Detection:** If identities do not match, `verify_setup.py` now fails with a clear error: `Identity check: identity1 = <gcloud_id>, identity2 = <adc_id>`.
- **Authentication Documentation:** Added a dedicated "Authentication" section to `SKILL.md` with instructions on how to sync identities using `gcloud auth application-default login`.

### Changed
- Refined `SKILL.md` terminology for better clarity on ADC vs. gcloud CLI authentication.

### Author
- Riccardo

---

## [0.0.1] - 2026-03-20
### Added
- Initial implementation of the OneMCP setup skill.
- Support for Cloud Logging, Developer Knowledge, Firestore, and BigQuery MCP servers.
- Automated API enabling and API key generation.
- Basic `verify_setup.py` for checking MCP server availability.
