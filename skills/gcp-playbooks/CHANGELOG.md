# Changelog: GCP Playbooks Skill

All notable changes to this skill will be documented in this file.

## [0.0.2] - 2026-04-08
### Added
- Added `wietse_cloud_run_error_reporter.py` script (moved from `cloud_logging` skill).
- Created `scripts/` directory for skill-specific utilities.

## [0.0.1] - 2026-04-02
### Added
- Initial setup of the `gcp-playbooks` skill.
- Established a deterministic directory structure: `references/googleapis.com/<service>.md`.
- Added API Name header to each playbook file.
- Consolidated and mapped Infrastructure Discovery asset types (e.g., `run.googleapis.com/Service`, `storage.googleapis.com/Bucket`) in `cloudresourcemanager.md`.
- Added `README.md` as a high-level index for playbooks.
- Added placeholders and generic mitigation mappings for Cloud Build (`cloudbuild.md`) and Cloud Resource Manager (`cloudresourcemanager.md`).
- Added Cloud Run (`run.md`) and GKE (`container.md`) playbooks mapping generic mitigations to actuations (tracked by b/498849864).
- Tracked by b/498511917.
