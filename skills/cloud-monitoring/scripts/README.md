# Scripts Manual

This directory contains standalone utility scripts for the `cloud_monitoring` skill.

## `setup-frontend-slo.sh`

This bash script automates the creation of a **Service Level Objective (SLO)** based on **Log-based Metrics** for a Google Cloud project. It's particularly useful for demo environments (like the `microservices-demo` frontend).

### What it does:
1. **Creates Log-based Metrics**: 
   - `frontend_total_requests`: Counts all logs from the `frontend` pod.
   - `frontend_error_requests`: Counts logs from the `frontend` pod that are either `severity >= ERROR` or contain an "http response code: 5" payload.
2. **Discovers the Monitoring Service**: Automatically finds the first custom "Service" registered in Cloud Monitoring for the active GCP project.
3. **Creates the SLO**: Generates a 99.9% availability SLO over a 28-day rolling period. It calculates availability as `(Total Requests - Error Requests) / Total Requests`.

### Prerequisites
- You must be authenticated to GCP (`gcloud auth login` / `gcloud config set project <PROJECT_ID>`).
- A Custom Service must already exist in Cloud Monitoring (the script will fail if it can't find one).
- Note: It expects you to manually handle metrics deletion if they already exist (the deletion lines are commented out by default to avoid accidental destruction).

### Usage
```bash
./setup-frontend-slo.sh
```

## `export_timeseries_to_csv.py`
*(See `SKILL.md` for primary usage instructions on this script.)*
