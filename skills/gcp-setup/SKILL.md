---
name: gcp-setup
description: 🐉 Initial Google Cloud environment verification and authentication setup. Use when starting a new session to ensure correct identities across gcloud, ADC, and kubectl.
metadata:
  author: Google
  version: 0.0.2
---

# GCP Environment Setup

Use this skill to verify and harmonize your GCP identities at the start of an investigation or session.

## Core Workflow

1.  **Identity Verification**: Run the bundled `gcp-whoami.sh` script to check all three major identities (gcloud, ADC, and kubectl).
2.  **Harmonization**: If identities mismatch, offer to fix them.
    *   To fix `gcloud`: `gcloud auth login [ACCOUNT]`
    *   To fix ADC: `gcloud auth application-default login`
    *   To fix GKE/kubectl: `gcloud container clusters get-credentials [CLUSTER] --region [REGION] --project [PROJECT]`
3.  **🛑 MANDATORY Next Step: Architecture Discovery**: Once identities are verified and correct, check if the `./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}` directory exists. If it is missing or empty, you **MUST** immediately transition to the `gcp-architecture-discovery` skill and explicitly instruct it to execute a full baseline discovery to sweep and map the entire infrastructure state.

## Bundled Scripts

- `scripts/gcp-whoami.sh`: Displays current identities for gcloud, ADC, and kubectl.

## Safe Mode Support

If `SAFE_MODE="enabled"` is found in the environment or `.env` file, you MUST activate the `safe-sre-investigator` skill immediately after verifying the initial setup. This ensures all subsequent operations use read-only/non-mutating service accounts.

Note that the `SAFE_MODE` might impact kubectl authorization via RBAC. 