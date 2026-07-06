# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.20] - 2026-06-25

### Added

- **GitHub Copilot CLI support**: Added `.copilot-plugin/plugin.json` (Copilot-specific plugin manifest) and `.copilot-plugin/marketplace.json` (canonical Copilot marketplace location).
- **Justfile**: New `install-copilot` (local dev install) and `install-copilot-persistent` (marketplace install) recipes.
- **Documentation**: Updated `INSTALL.md` with a GitHub Copilot CLI installation section (Option A — local, Option B — marketplace). Updated `README.md` compatibility table and quickstart to include Copilot CLI.

## [0.1.19] - 2026-06-15

### Changed

- **GitHub Actions**: Opted into Node.js 24 for all workflows by setting `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: 'true'`. Updated `actions/github-script` to `v8.0.0` to resolve deprecation warnings.

## [0.1.18] - 2026-06-15

### Fixed

- **Gemini CLI GHA Integration**: Resolved issue #37 by correcting GitHub MCP tool names (`get_issue`, `get_pull_request`, etc.) in TOML prompts and workflow YAML configurations. Switched from Docker to `npx` for the GitHub MCP server to improve reliability and performance in GitHub Actions.

## [0.1.17] - 2026-06-09

### Changed

- **Documentation**: Updated walkthrough video links and environment configurations for workspace trust.

## [0.1.16] - 2026-06-05

### Added

- **Architecture Discovery Skill**: Added the `gcp-architecture-discovery` skill (`skills/gcp-architecture-discovery/`) to discover and map GCP infrastructure architecture including compute, networking, storage, and service dependencies.

### Changed

- **Entrypoint & Setup Orchestration**: Updated `gcp-setup` and `investigation-entrypoint` skills to integrate the new architecture discovery workflow as a mandatory baseline and incremental investigation step before performing queries or log analysis.

## [0.1.15] - 2026-06-02

### Changed

- **Outage Demo Video Thumbnail**: Swapped the demo video preview to use a stunning custom screenshot (`docs/sre-demo-video-thumbnail.png`) showing the active multi-endpoint availability graph and SRE checklist for maximum visual impact.

## [0.1.14] - 2026-06-02

### Added

- **Outage Demo Video**: Embedded a high-quality video link at the top of `README.md` showcasing a live SRE investigation and PostMortem generation with the extension.
- **Installation Walkthrough Video**: Added a step-by-step video guide card at the top of `INSTALL.md` to help users get set up quickly.

## [0.1.13] - 2026-06-01

### Changed

- **Investigation Entrypoint**: Added guidelines instructing the Investigator to automatically leverage sparklines and ASCII/Unicode graphs (`export_timeseries_to_csv.py` or `csv_to_sparkline.py`) alongside start/end timestamp context to give the user a rapid visual overview of incident metrics.

## [0.1.12] - 2026-05-29

### Added

- **Harness Compatibility Matrix**: Introduced a comprehensive client capability and support matrix directly in `README.md`, clarifying feature coverage (installation, GCP MCP setup, and general SRE capabilities) across Gemini CLI, Antigravity CLI, Claude Code, and OpenAI Codex.

## [0.1.11] - 2026-05-29

### Changed

- **just install-agy**: Enhanced the recipe to output a clean, green success emoji showing the installed version on first-time installation as well, matching the second-time check output.

## [0.1.10] - 2026-05-28

### Added

- **just plugin-version**: Exposed a parameterized recipe that retrieves the version from any plugin JSON manifest file.
- **test/get_plugin_version.sh**: Added a robust helper bash script to extract version info from any JSON file using `jq` (with a zero-dependency fallback to `grep` and `sed`).
- **OneMCP Support for Antigravity**: Refactored `gcp-mcp-setup` skill and `setup_onemcp.py` to seamlessly configure modern Antigravity CLI and Editor paths.
- **Structured Reference Templates**: Created structured `settings.json` (Gemini CLI) and `mcp_config.json` (Antigravity) schemas under `skills/gcp-mcp-setup/references/`.

### Changed

- **just install-agy**: Improved the recipe to check for an existing installation, compare the installed version with the workspace version, and print a warning or success message indicating whether they are in sync (e.g., `0.1.9 vs 0.1.10`).
- **OneMCP Output Optimization**: Modified the config generator to write tailored settings keys (`httpUrl` for Gemini and `serverUrl` for Antigravity) to prevent diagnostic key pollution.

## [0.1.9] - 2026-05-28

### Added

- **Automated Validation Tests**: Created a unified test runner `test/run_tests.sh` that checks version consistency across manifests (`test/check_manifest_versions.py`) and ensures skills frontmatter conforms to specifications.
- **just test**: Added a `just test` recipe to easily execute all validation checks with a single command.

### Fixed

- **Skill Frontmatter**: Quoted name/description fields, added missing emojis, and aligned statuses to satisfy metadata schema requirements across multiple skills.

## [0.1.8] - 2026-05-28

### Added

- **just install-agy**: Added a `just install-agy` recipe to automate cloning the SRE extension repository directly into the `agy` plugins directory (`~/.gemini/config/plugins/sre-extension`).
- **just install-geminicli**: Added a `just install-geminicli` recipe to install the extension via the Gemini CLI extensions command.
- **just install-claude**: Added a `just install-claude` recipe to run Claude Code pointing to this plugin directory.

## [0.1.7] - 2026-05-22

### Added

- **Plugin Manifest**: Added `plugin.json` at the root of the repository to support plugin integration and discovery as a named SRE extension.
- **Claude Plugin Support**: Added `.claude-plugin/plugin.json` to enable native compatibility with Claude Code plugins.
- **Codex Plugin Support**: Added `.codex-plugin/plugin.json` to enable native compatibility with OpenAI Codex plugins.
- **Documentation**: Updated `README.md` and `USER_MANUAL.md` with installation and loading guides for Antigravity, Claude Code, and OpenAI Codex plugin systems.

### Changed

- **Extension Config**: Bumped extension metadata version to `0.1.7` in `gemini-extension.json`.

## [0.1.6] - 2026-04-20

### Added

- **Monitoring Graphs**: Extracted `csv_to_sparkline.py` to autogenerate Unicode sparklines wrapped in pipes for better spacing visibility on arbitrary CSVs.

### Changed

- **Cloud Monitoring**: Refactored the terminal statistics to adopt the 'Sparkline' naming convention and use the pipe encapsulation framework.

## [0.1.5] - 2026-04-17

### Added

- **Cloud Monitoring**: Added 'gist' / 'graphical shape' feature to visually represent time-series data.

## [0.1.4] - 2026-04-17

### Added

- **New Skill**: `postmortem-aggregator` (v0.0.1) moved from `gemini-cli-custom-commands`.

### Changed

- **Merged Skills**: Consolidated `postmortem-generator-copy` and the external `postmortem-generator` into a single `postmortem-generator` skill (v0.0.5).
  - Improved the merged `SKILL.md` with combined IRM examples (Google IRM, ServiceNow, JIRA, etc.) and better execution instructions.
  - Standardized directory structure for postmortem output.

## [0.1.3] - 2026-04-16

### Added

- **GitHub Actions Integration**:
  - Added workflows for issue triage, PR review, and automated planning/execution.
  - Configured custom Gemini CLI commands for GHA environment (`gemini-invoke`, `gemini-plan-execute`, etc.).

## [0.1.2] - 2026-04-16

### Changed

- Moved `policy.toml` to `policies/` directory for better organization.

## [0.1.1] - 2026-04-16

### Changed

- **Pre-publication Cleanup**:
  - Replaced internal email addresses with GitHub profile links in `README.md` and skill metadata.
  - Removed internal `go/` shortlinks and `/google/` infrastructure paths. <!-- pre-publish-checker: ignore -->
  - Moved internal-only `TODO`s to untracked local files. <!-- pre-publish-checker: ignore -->
  - Restricted experimental `agents/` directory from the public repository.
- **Improved Tooling**:
  - Added a `pre-publish-checker` skill with automated scripts for scanning profanity, internal links, and professionalism.
  - Added a synopsis script for tracking publication readiness.

## [0.1.0] - 2026-04-14

### Added

- **New Skills**:
  - `cloud-logging`: Analyze GCP JSON logs and convert to Apache format.
  - `cloud-monitoring`: Export time-series data to CSV and setup frontend SLOs.
  - `monitoring-graphs`: Generate high-quality annotated incident graphs using Python.
  - `anomaly-detection`: Detect anomalies using Isolation Forest, KNN, and Z-score.
  - `data-ingestion`: Merge and parse time-series data from various sources.
- **Validation Tools**:
  - New `test/check_skills_frontmatter.py` script to enforce skill standards (names, descriptions, dragon emojis 🐉).
  - Added `--no-warnings` and `--verbose` flags to the skills validator.
  - Integrated `justfile` targets for linting and cross-project checks.
- **Documentation**:
  - Added `docs/sre-extension-logo.png` and integrated it into the `README.md`.
  - Updated `docs/SKILLS-STANDARDS.md` with strict naming and frontmatter requirements.

### Changed

- Reorganized skills folder structure to use dashes instead of underscores.
- Renamed `postmortem-generator-copy` to `postmortem-generator` after reconciliation.
- Standardized all skill names and descriptions to pass strict frontmatter validation.

### Removed

- Cleaned up old migration documentation (`docs/MIGRATION_META_PLAN.md`, etc.).

## [0.0.5] - 2026-04-13

### Added

- Added Apache 2.0 LICENSE file.
- Moved `docs/user-manual.md` to root `USER_MANUAL.md` for better visibility.

## [0.0.4] - 2026-04-02

### Added

- Initialized `gcp-playbooks` skill (v0.0.1) to provide SRE playbooks for GCP/GKE investigations.
- Added `CONTRIBUTING.md` with open-source and Google best practices.
- Documented cross-project discovery using `gcloud asset search-all-resources`.
- Tracked by b/498511917 and b/498849864.

### Changed

- Refined `GEMINI.md` and `README.md` with updated contributor info and Gerrit best practices.
- Reorganized `gcp-playbooks` reference structure for better determinism and DRYness.

## [0.0.3] - 2026-03-30

### Added

- Added optional `--google-maps-key` flag to `gcp-mcp-setup` to configure `google-maps` MCP server.
- Added identity consistency check (gcloud vs ADC) to `gcp-mcp-setup` verification script.

### Changed

- Refactored `gcp-mcp-setup` testing: consolidated bash scripts into a single comprehensive Python verification script (`verify_setup.py`).
- Improved `gcp-mcp-setup` setup script to use explicit flags (`--local` / `--global`) for safer settings injection.

## [0.0.2] - 2026-03-30

### Added

- Added OneMCP setup skill (v0.0.1) to automate the configuration of Google Managed MCP servers.
- Migrated OneMCP setup script to Python for safer JSON injection.
- Added BigQuery and Firestore MCPs back into the OneMCP setup script.

## [0.0.1] - 2026-03-25

### Added

- Created the core Migration Meta Plan to move from internal tools to open-source GCP/GKE tooling.
- Configured GCP/GKE specific guidelines and OneMCP constraints in `GEMINI.md`.
- Initialized `agents/outage-investigator.md` tuned for Cloud Logging, Cloud Monitoring, and GKE cluster response.
- Introduced a Mitigation Taxonomy for mapping incident mitigation strategies to GCP/GKE actions.
- Included `gemini-extension.json` for custom script-based MCP integrations.
- Integrated `skaffold` as the primary tool for testing codebase-level deployment mitigations.
