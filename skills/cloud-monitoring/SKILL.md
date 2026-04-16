---
name: cloud-monitoring
description: 🐉 Skill for interacting with Google Cloud Monitoring (CM) via APIs to avoid large context bloat. Produces nice short synoptic "gists" of graphs
version: 0.2.16
tools:
  - mcp_google-monitoring_get_alert
  - mcp_google-monitoring_get_alert_policy
  - mcp_google-monitoring_get_dashboard
  - mcp_google-monitoring_list_alert_policies
  - mcp_google-monitoring_list_alerts
  - mcp_google-monitoring_list_dashboards
  - mcp_google-monitoring_list_metric_descriptors
  - mcp_google-monitoring_list_timeseries
  - mcp_google-monitoring_query_range
---

# Cloud Monitoring

> **⚠️ PREREQUISITE: `google-monitoring` MCP Server**
> This skill relies on the `google-monitoring` MCP server being installed and active. Before proceeding with monitoring tasks, assert that the required MCP tools (e.g., `mcp_google-monitoring_query_range`) are available. If they are missing, immediately inform the user and recommend they enable the MCP server (they can use the `gcp-mcp-setup` skill if available).

This skill provides utilities for analyzing and extracting data from Google Cloud Monitoring (CM). 

## Best Practices

* **Avoid Context Bloat:** Cloud Monitoring API responses can be massive. Do not try to read raw JSON responses directly into the LLM context. Try to delegate to a SubAgent anything which pulls monitoring data as they tend to bloat the context.
* **Use Export Scripts:** If you pull monitoring data, make sure to surface this final data (in CSV format) using the `scripts/export_timeseries_to_csv.py` Python script to surface important stats like AVG, Max, Min and a simplified text-graph of the system (see `references/sample_output_dual_metrics.csv`) . Also report back that stats header to the main agent, together with any interesting insights you might have found.
* **Metadata Headers:** Exported data should contain metadata (time ranges, metric names) at the top of the file so that the context of "when" the data was pulled is never lost, as `now()` changes over time.
* **Target Workloads:** Focus your monitoring extractions primarily on GKE and Cloud Run environments. Generic time-series extractions should still allow filtering by specific resources.
* **Paired Metrics Comparison:** The extraction script supports querying multiple metrics simultaneously. For apples-to-apples comparisons, try these recommended pairs:
  * **Network I/O:** `compute.googleapis.com/instance/network/received_bytes_count` vs `compute.googleapis.com/instance/network/sent_bytes_count`
  * **Disk I/O:** `compute.googleapis.com/instance/disk/read_bytes_count` vs `compute.googleapis.com/instance/disk/write_bytes_count`
  * **Cloud Run Traffic:** `run.googleapis.com/request_count` vs `run.googleapis.com/response_latencies`
  * **GKE Memory vs CPU:** `kubernetes.io/container/memory/used_bytes` vs `kubernetes.io/container/cpu/core_usage_time`

## Available Tools

* `scripts/export_timeseries_to_csv.py`: Fetches time-series data for specified metric(s) and time range, outputting a CSV file with metadata headers. Supports extracting two or more variables for direct correlation and comparison. This is an amazing synoptic you can surface to the user
    * It's very effective particularly to share the "**gist**" / **Shape** part showing use in TEXT the graphical shape of the curve, eg "█▇▆▇ ▂▃ ▂ ▂ ▂ ▂" or "█▆▃▂▄▅▅_▄▄▄▂▄▄█▆". This is very useful to humans for visual feedback!
* `scripts/setup-frontend-slo.sh`: A bash script to automatically set up a 99.9% availability SLO using Log-based Metrics for a 'frontend' service. (See `scripts/README.md` for full manual).
