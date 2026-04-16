---
name: gcp-slo-management
description: 🐉 [SRE] Manage Service Level Objectives (SLOs) on Google Cloud. Use when you need to discover Monitoring Services, list existing SLOs, or create new SLOs (Availability/Latency) via the REST API when gcloud commands are unavailable.
---

# GCP SLO Management

## Overview

This skill enables the discovery and management of SLOs in Google Cloud Monitoring. Since `gcloud` lacks native SLO creation commands, this skill leverages the Monitoring REST API and a bundled discovery script.

## Core Pattern

### 1. Discover Services
Every SLO must be attached to a **Service**. Use the discovery script to find the correct `Service ID`.
- **Command**: `python3 skills/gcp-slo-management/scripts/discovery.py <PROJECT_ID>`
- **Output**: A table showing `Display Name` and `Service ID`.

### 2. Create an SLO
Use `curl` to POST a JSON definition to the service.

#### Example: 99% Availability (7-day rolling)
```bash
# Set variables
PROJECT_ID="your-project"
SERVICE_ID="wl:..." # From step 1
TOKEN=$(gcloud auth application-default print-access-token)

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://monitoring.googleapis.com/v3/projects/$PROJECT_ID/services/$SERVICE_ID/serviceLevelObjectives" \
  -d '{
    "displayName": "99% Availability - Last 7 Days",
    "goal": 0.99,
    "rollingPeriod": "604800s",
    "serviceLevelIndicator": {
      "basicSli": {
        "availability": {}
      }
    }
  }'
```

## Advanced Patterns

- **Custom Services**: For services not automatically discovered (e.g., frontend logs), you must use `requestBased` or `windowBased` SLIs with specific metric filters.
- **Latency SLOs**: Requires defining a `latency` threshold within `basicSli`.

## Troubleshooting
- **403 Forbidden**: Ensure you have run `gcloud auth application-default login` and that your account has `roles/monitoring.editor`.
- **Service Not Found**: Use the discovery script to verify the `Service ID` exists in the target project.
