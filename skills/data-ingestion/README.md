# Data Ingestion Skill

This skill fetches and parses time-series data from various sources and returns it in a standardized JSON format.

## Usage

To use this skill, specify the `source_type` and `source_details`.

**Example for single CSV:**

```
/use_skill data_ingestion source_type="csv" source_details=["/path/to/your/data.csv"]
```

**Example for multiple CSVs:**

```
/use_skill data_ingestion source_type="csv" source_details=["/path/to/metric1.csv", "/path/to/metric2.csv"]
```

## Supported Source Types

-   `csv`: Expects `source_details` to be a list of file paths. Each CSV file should contain two columns: `timestamp` and a metric value. The header of the second column is used as the metric name.

## Standardized JSON Output Format

The skill returns a single JSON object with the following structure, merging data from all provided files:

```json
{
  "metadata": {
    "source_type": "csv_merged",
    "source_details": ["/path/to/metric1.csv", "/path/to/metric2.csv"],
    "available_metrics": ["metric1", "metric2"]
  },
  "columns": ["timestamp", "metric1", "metric2"],
  "timeseries": [
    ["2026-04-04T18:00:00Z", 10.5, 20.1],
    ["2026-04-04T18:00:10Z", 12.3, null],
    ["2026-04-04T18:00:20Z", null, 20.2]
    // ... more [timestamp, value1, value2] pairs
  ]
}
```

-   Timestamps are aligned across all files.
-   If a metric doesn't have a value for a specific timestamp, it's represented as `null`.
