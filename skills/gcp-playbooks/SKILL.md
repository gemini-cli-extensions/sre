---
name: gcp-playbooks
description: 🐉 [SRE] Use when you need to follow established SRE playbooks for GCP/GKE investigations, including infrastructure discovery and common mitigation steps.
author: Riccardo
version: 0.0.2
status: draft
---

# GCP SRE Playbooks

## Overview

This skill provides a collection of playbooks and reference materials for SREs to investigate and mitigate incidents on Google Cloud Platform. It focuses on mapping generic SRE concepts (discovery, mitigation, postmortem) to specific GCP/GKE actions.

## Naming Convention

Playbooks follow a deterministic naming convention based on the GCP API service name, located in the `references/googleapis.com/` directory. 
Example: `run.md` (for `run.googleapis.com`).
Each file should also explicitly list the full API name at the top.

## When to Use

- When starting an investigation and needing to discover the infrastructure.
- When following a specific mitigation strategy (e.g., rollback, traffic shifting).
- When a user asks for "GCP playbooks" or "SRE playbooks".

## Available Playbooks

### 1. Infrastructure Discovery

Located at `skills/gcp-playbooks/references/googleapis.com/README.md`. 
Use this to systematically identify the resources involved in an incident.

### 2. Cloud Run Mitigations

Located at `skills/gcp-playbooks/references/googleapis.com/run.md`.
Maps generic mitigations (rollback, fix forward, upsize, restart) to Cloud Run actions.

### 3. GKE Mitigations

Located at `skills/gcp-playbooks/references/googleapis.com/container.md`.
Maps generic mitigations (rollback, fix forward, upsize, quarantine, restart) to GKE / Kubernetes actions.

### 4. Cloud Build Investigation (Draft)

Located at `skills/gcp-playbooks/references/googleapis.com/cloudbuild.md`.

## Core Pattern

1. **Identify the Scope**: Use `gcp_resource_manager` or the discovery playbook to find the relevant project and resources.
2. **Consult the Playbook**: Look for a matching playbook in `references/googleapis.com/` using the short API name.
3. **Execute Actions**: Follow the gcloud/kubectl commands suggested in the playbook.
4. **Validate**: Verify the state of the system after each action.

## References

- [GCP Documentation](https://cloud.google.com/docs)
