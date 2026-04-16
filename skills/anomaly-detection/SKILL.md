---
name: anomaly-detection
description: 🐉 Detects anomalies in time-series data from various sources.
---

# Anomaly Detection Skill

You are an expert SRE Detective. Your job is to analyze time-series metrics and pinpoint anomalous behavior with minimal user friction.

**Inputs:**

*   `source_type`: String indicating the data source (e.g., "csv", "cloud_monitoring").
*   `source_details`: A dictionary or list containing the necessary information to access the data source.
    *   For `source_type: "csv"`: A list of file paths.
*   `context`: (Optional) String, either free-form text describing the issue or an issue tracker ID like a GitHub issue or Jira ticket.
*   `metrics`: (Optional) List of strings, specific metric names to analyze from the source.
*   `smoothing`: (Optional) String, method for smoothing (e.g., "moving_average", "exponential"). USER OVERRIDE.
*   `window`: (Optional) Integer, window for moving average. USER OVERRIDE.
*   `alpha`: (Optional) Float, alpha for exponential smoothing. USER OVERRIDE.
*   `algorithm`: (Optional) String, anomaly detection algorithm (e.g., "knn", "zscore", "isolation_forest"). USER OVERRIDE.
*   `n_neighbors`: (Optional) Integer for KNN detector. USER OVERRIDE.
*   `threshold`: (Optional) Float, for Z-Score. USER OVERRIDE.
*   `contamination`: (Optional: Float or "auto") For Isolation Forest. USER OVERRIDE.

**Workflow:**

1.  **Get Data:**
    *   Call `@skills/data_ingestion` with `source_type` and `source_details`.
    *   Save output to `.gemini/tmp/user/merged_data.json`.

2.  **Select Metrics:** (Same as before - infer from query/context, ask if needed)
    *   Let `available_metrics` be `metadata.available_metrics` from `merged_data.json`.
    *   If `metrics` input is provided, validate they are in `available_metrics`. Use these valid metrics.
    *   If `metrics` input is NOT provided, analyze the user's initial query and `context` for metric names. Try to match keywords with `available_metrics`.
    *   If no clear metrics can be inferred, or if there's ambiguity, use `ask_user` to prompt the user to select one or more metrics from `available_metrics`.
    *   Let `selected_metrics` be the list of metrics to analyze.

3.  **Process Each Selected Metric:** Iterate through each `metric_name` in `selected_metrics`:

    a.  **Filter Metric Data:** Create a temporary JSON file (`/tmp/single_metric_data.json`) containing only the "timestamp" and the current `metric_name` column from `merged_data.json`. You can write a short Python script to extract the relevant column based on the metric index in the `"columns"` list, ignoring rows where the metric value is `null`.

    b.  **Automated Preprocessing:**
        *   **Check for User Override:** If `smoothing` parameter is provided, use the specified method and parameters.
        *   **Automated Choice:** If no override, the agent should *autonomously* decide if smoothing is needed. Heuristic: calculate the point-to-point change percentage. If a significant number of points exceed a threshold (e.g., >20% change), apply a default `moving_average` with a small window (e.g., 3 or 5).
        *   Log the decision: "No smoothing applied" or "Applied Moving Average smoothing with window=3".
        *   If smoothing is applied, run `scripts/preprocess_data.py` as before, outputting to `/tmp/preprocessed_data.json`.
        *   Input to next step is `/tmp/preprocessed_data.json` or `/tmp/single_metric_data.json`.
        *   Let this be `data_for_detection.json`.

    c.  **Automated Algorithm Selection:**
        *   **Check for User Override:** If `algorithm` parameter is provided, use the specified algorithm.
        *   **Automated Choice:** Default to `isolation_forest` as it's generally robust. Contamination set to "auto".
        *   Let `chosen_algorithm` be the selected method.

    d.  **Detect Anomalies:** Execute the script for `chosen_algorithm`:
        *   All detection scripts take `data_for_detection.json` as input and output to `/tmp/detected_data.json`.
        *   **Example (Isolation Forest):**
            ```bash
            source $HOME/.venvs/sre-extension-anomaly-detection/bin/activate &&
            python3 .gemini/skills/anomaly_detection/scripts/detect_isolation_forest.py \
            /tmp/data_for_detection.json --contamination auto \
            > /tmp/detected_data.json
            ```
        *   Adjust command and parameters for knn or zscore if overridden.

    e.  **Evaluate Noise & Auto-Tune (Self-Reflection) - MANDATORY:**
        *   **Requirement:** You MUST evaluate the noise level of the detection result for EVERY metric, without exception.
        *   **Calculation:** Use `jq` to count the total points and the anomaly points in `/tmp/detected_data.json`.
        *   **Noise Threshold:** If the anomaly count exceeds **5%** of the total data points, the result is considered "noisy" (false positives).
        *   **Autonomous Fallback:** If noisy, you MUST discard the result, log "Detection too noisy ({count} anomalies), applying autonomous auto-tuning", and loop back to **Step 3.b**.
        *   **Auto-Tune Parameters:** Force **Smoothing** to `moving_average` (window=5) and **Algorithm** to `zscore` (threshold=3.0).
        *   **Quality Check:** After re-running, ensure the new result is within reasonable bounds (e.g., < 2% of points). If still noisy, increase the Z-Score threshold iteratively (e.g., to 4.0 or 5.0) until the signal is clear.

    f.  **Plot Anomalies:** Execute `scripts/plot_anomalies.py` and move the output to the destination directory.
        *   **Example:**
            ```bash
            PLOT_FILE=$(python3 .gemini/skills/anomaly_detection/scripts/plot_anomalies.py /tmp/detected_data.json) &&
            mkdir -p data && mv "$PLOT_FILE" data/${metric_name}_anomalies.png
            ```

    g.  **Extract Results Summary:** Use `jq` to extract the exact timestamps where an anomaly was detected to summarize the findings.
        *   **Example:**
            ```bash
            jq -r '.timeseries[] | select(.[2] == true) | .[0]' /tmp/detected_data.json | head -n 5
            ```

4.  **Correlate & Explain:** Synthesize the detected anomalies, matching up the time windows across multiple metrics. Explain which anomalies correlate and what the underlying cause might be.

5.  **Report Results:** Provide a clear summary to the user including the algorithm used, any preprocessing applied, the time windows of the anomalies, and the path to the generated plots.
