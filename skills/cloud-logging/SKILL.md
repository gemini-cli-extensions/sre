---
name: cloud-logging
description: 🐉 Skill for interacting with and analyzing Google Cloud Logging and Error Reporting. Use this when you need to process large JSON logs from GCP or convert them to Apache format for easier analysis.
version: 0.3
---

# Cloud Logging 

This skill provides utilities for analyzing logs, errors, and system health across Google Cloud deployments.

* Prioritize Logs with `severity` >= "ERROR" as they tend to be less verbose.
* Constrain logs around the time of investigation (possibly going back a few hours/days to find smoking guns).


## Logs DOs and DONT's

Ingesting Logs into an LMM memory can easily saturate your context.

* [BAD] **DO NOT** ingest big files. Antipattern:  `ReadFile path/to/access_logs_raw.json`.
    * It's ok to get raw logs, but also use `jq` or scripts to read them without polluting your context window.
    * [GOOD] Use simple maniuplation like: `jq -r '.[] | .httpRequest.status'` to get a list of statuses.
    * [GOOD] Reduce size with scripts such as `scripts/cloudlogging2apachelogs.py <big_logfile.json>` (provided in the skill)
* [BAD] Do not call **long**-running calls without precautions, eg `gcloud logging read`
    * [GOOD] Rather prepend some reasonable `timeout 60 gcloud logging read ...`, or
    * [BEST] Use the `run_shell_command` tool with `is_background: true` and poll the results being dumped to file periodically.


## Bundled Scripts

### cloudlogging2apachelogs.py

Converts GCP Cloud Logging JSON exports into a format loosely resembling Apache Combined Log format. This is much more token-efficient for the LLM.

**Usage**:
```bash
python3 scripts/cloudlogging2apachelogs.py path/to/logs.json
```

**Testing**:
You can verify the script works by running its test:
```bash
python3 scripts/cloudlogging2apachelogs_test.py
```

## Bundled Assets

* `assets/sample_logs.json`: A small sample of GCP Cloud Logging JSON for testing conversion scripts.
