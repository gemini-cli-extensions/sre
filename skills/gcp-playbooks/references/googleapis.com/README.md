# Google APIs Playbooks Reference

This directory contains deterministic, API-specific playbooks for SRE investigations and mitigations on Google Cloud. 

## Infrastructure Discovery

For detailed guidance on discovering infrastructure, projects, and assets (including Cloud Run, GKE, Cloud SQL, and GCS), please refer to:

- [Cloud Resource Manager & Discovery Playbook](cloudresourcemanager.md)

This playbook explains how to use both `gcloud` and MCP tools for cross-project discovery, project state verification, and a comprehensive list of Cloud Asset Inventory asset types to look for.

To torubleshoot serving infra, refer to specific per-product playbooks:
- [Cloud Run](run.md)
- [GKE](container.md)
