---
name: data-ingestion
description: 🐉 Fetches and parses time-series data from various sources.
author: Szymon Stawski # + Gemini
version: 0.2.0
status: development
---

# Data Ingestion Skill

This skill is responsible for fetching and converting time-series data from different sources into a standardized JSON format for other skills to consume.

**Inputs:**

*   `source_type`: String indicating the data source (e.g., "csv", "cloud_monitoring").
*   `source_details`: A dictionary or list containing the necessary information to access the data source.
    *   For `source_type: "csv"`: A list of file paths.

**Output:**

A JSON string in the standardized format (see README.md for details).

**Workflow:**

1.  **Validate Inputs:** Check if `source_type` and `source_details` are provided.
2.  **Route to Parser:** Based on `source_type`:
    *   If `source_type` is "csv":
        *   Ensure `source_details` is a list of file paths.
        *   Create a list of temporary file names for intermediate JSON outputs (e.g., `~/.gemini/tmp/user/parsed_0.json`, ...).
        *   **Parse Each CSV:** Iterate through the input file paths:
            *   Execute `python ./skills/data-ingestion/parse_csv.py <input_csv_path> > <temp_json_path>` using `run_shell_command` (with venv activation).
            *   Check for errors.
        *   **Merge JSONs:** Execute `python ./skills/data-ingestion/merge_timeseries.py <temp_json_path_1> <temp_json_path_2> ...` using `run_shell_command` (with venv activation).
        *   Capture the stdout from `merge_timeseries.py` as the final result.
        *   **Clean up:** Remove the temporary JSON files.
        *   Handle any errors during script executions.
    *   If `source_type` is not supported, return an error message.
3.  **Return JSON:** Output the standardized JSON string.
