# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-04-16

### Changed

- Moved `policy.toml` to `policies/` directory for better organization.

## [0.1.1] - 2026-04-16

### Changed

- **Pre-publication Cleanup**:
  - Replaced internal email addresses with GitHub profile links in `README.md` and skill metadata.
  - Removed internal `go/` shortlinks and `/google/` infrastructure paths.
  - Moved internal-only `TODO`s to untracked local files.
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
