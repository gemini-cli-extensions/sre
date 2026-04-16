# Changelog - OneMCP Setup Skill

All notable changes to this skill will be documented in this file.

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
