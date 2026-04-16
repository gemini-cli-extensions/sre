# 📝 Changelog: investigation-entrypoint

All notable changes to the `investigation-entrypoint` skill will be documented in this file.

## [1.3.0] - 2026-04-07
### 🔄 The "Grand Unification" Update

- **Renamed Skill:** Changed the name from `incident-response` to `investigation-entrypoint` to make it explicitly clear that this is the primary starting point for handling any outage.
- **Merged Outage Investigator:** Absorbed all the high-quality technical debugging guidelines, root cause analysis (RCA) workflows, and GKE/Cloud Run checklists from the deprecated `outage-investigator` skill.
- **Unified Workflow:** The skill now provides a complete end-to-end flow: Context Gathering & Orchestration ➡️ Data Collection & Deep Dive ➡️ Root Cause Analysis ➡️ Mitigation Strategy & Actuation.
- **Incident Management Stack Preserved:** Kept the existing orchestration logic for PagerDuty, ServiceNow, and Native GCP incident management.

## [1.1.0] - 2026-04-07
### 🛠️ Pre-Merge State
- Original `incident-response` capabilities including mitigation taxonomy (Rollback, Throttling, etc.) and risk assessment instructions.
