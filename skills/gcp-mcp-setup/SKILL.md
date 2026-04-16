---
name: gcp-mcp-setup
version: 0.0.8
author: Riccardo
description: 🐉 [SRE] Use when the user wants to set up Google Managed MCP (OneMCP) servers for their Gemini CLI environment. Automates enabling services, MCP servers, generating API keys, and configuring ~/.gemini/settings.json.
---

# OneMCP Setup Skill

## Overview

This skill provides the automated steps to configure your environment and enable the **Core Google Managed MCP servers** (Logging, Monitoring, GKE, Run, Resource Manager, Developer Knowledge) by default. Use the `--all` flag to include additional services like Error Reporting, Cloud SQL, Spanner, Pub/Sub, Vertex AI, Firestore, and BigQuery.

## When to Use

Use this skill when the user asks to "install OneMCP", "setup OneMCP", or "configure Google Managed MCP servers".

## Core Pattern

1. **Prerequisites Verification**: Ensure the user has `gcloud` authenticated and a target Google Cloud Project with billing enabled.
2. **Setup Script Execution**: Run the provided script to enable APIs, MCP services, and generate the required API Key. 
   - By default, it installs a **Lean SRE toolset** (Logging, Monitoring, GKE, Run, Resource Manager, Developer Knowledge).
   - Use the `--all` flag to include optional services (Error Reporting, Databases, Vertex AI).
   - Script: `skills/gcp-mcp-setup/scripts/setup_onemcp.py <PROJECT_ID> [--local | --global] [--all] [--google-maps-key YOUR_KEY]`
3. **Configure Settings**: The script securely injects the JSON configuration directly into `.gemini/settings.json` if `--local` is provided, or `~/.gemini/settings.json` if the `--global` flag is provided. This prevents accidental overwriting of existing settings. The script requires one of these flags explicitly.
4. **Verification & Diagnostics:**
   - Script: `skills/gcp-mcp-setup/scripts/verify_setup.py`
   - This script runs `gemini -p "/mcp list"` and asserts that the OneMCP servers are configured and identifies identity mismatches.
   - For direct endpoint diagnostics (without Gemini), use the curl-based tool:
     - Script: `skills/gcp-mcp-setup/scripts/test_mcp_endpoint.sh [ENDPOINT_URL]`
     - Example: `./skills/gcp-mcp-setup/scripts/test_mcp_endpoint.sh https://monitoring.googleapis.com/mcp`

## Examples

User: "Please install OneMCP on my project my-gcp-project"
Agent: "I will use the gcp-mcp-setup skill to configure your project and Gemini settings for Cloud Logging, Developer Knowledge, Firestore, and BigQuery."

## Authentication

Note that the **gcloud CLI Identity** (how you are currently logged in via `gcloud auth login`) may differ from the **MCP Server Identity** (which is based on Application Default Credentials, or ADC).

MCP servers typically use ADC to authenticate. If these identities do not match, you may encounter permission errors (e.g., `serviceusage.serviceUsageConsumer` denied) even if `gcloud` commands work correctly.

If MCP doesn't work, yhou can poropose to run this on user's behalf: `gcloud auth application-default login --account <PROPOSED_IDENTITY_EMAIL>`
                                                                                                                                                          
### 💡 Path Forward

If you encounter an identity mismatch:
1. Run `gcloud auth application-default login --account=YOUR_CLI_IDENTITY` to synchronize identities.
2. Verify the identities match by running the verification script: `python3 skills/gcp-mcp-setup/scripts/verify_setup.py`.

## Documentation

- Code samples from Romin Irani: https://github.com/rominirani/google-mcp-servers/blob/main/demos/README.md
- All supported products: https://docs.cloud.google.com/mcp/supported-products
