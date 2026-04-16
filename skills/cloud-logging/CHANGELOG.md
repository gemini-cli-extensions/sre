# Changelog: Cloud Logging Skill

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-04-08

### Changed
- Bumped version to 0.2.
### Removed
- Relocated `tmp_weitse_pending_approval.py` (Cloud Run error reporter) to `gcp-playbooks` skill for better organization.

## [0.1.0] - 2026-04-02

### Added
- Initial setup of the `cloud_logging` skill.
- Added basic SKILL.md and scripts directory.
- Included `tmp_weitse_pending_approval.py` for Cloud Run revision error correlation.
