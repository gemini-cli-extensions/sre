#!/usr/bin/env -S uv run
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-cloud-monitoring",
#     "google-auth",
#     "python-dateutil",
#     "numpy",
# ]
# ///

"""
export_timeseries_to_csv.py: Extracts Google Cloud Monitoring data to CSV with embedded metadata and statistics.

Usage:
  ./export_timeseries_to_csv.py --project <PROJECT_ID> --metric_names <METRIC_1> [<METRIC_2> ...] [--output <FILE.csv>] [--from <ISO8601_OR_HOURS>] [--to <ISO8601>]

Example:
  ./export_timeseries_to_csv.py --project sre-next --metric_names "kubernetes.io/container/cpu/core_usage_time" "kubernetes.io/container/memory/used_bytes" --from "2 hours ago"
"""

import argparse
import csv
import sys
import os
import numpy as np
from datetime import datetime, timedelta, timezone
from google.cloud import monitoring_v3
import google.auth
from dateutil import parser

def parse_time(time_str, default_time=None):
    if not time_str:
        return default_time
    
    # Handle simple "X hours ago" or just an integer representing hours for convenience
    time_str = time_str.lower().strip()
    if time_str.endswith("hours ago") or time_str.endswith("hour ago") or time_str.isdigit():
        try:
            hours = int(time_str.split()[0])
            return datetime.now(timezone.utc) - timedelta(hours=hours)
        except ValueError:
            pass
            
    try:
        dt = parser.parse(time_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as e:
        print(f"Error parsing time '{time_str}': {e}", file=sys.stderr)
        sys.exit(1)

def get_position_label(index, total):
    if total <= 1:
        return "ONLY"
    if index == 0:
        return "START"
    if index == total - 1:
        return "END"
    pct = (index / (total - 1)) * 100.0
    return f"MIDDLE, {pct:.1f}%"

def generate_sparkline(vals, num_bins=16):
    if len(vals) == 0:
        return ""
    if len(vals) < num_bins:
        num_bins = len(vals)
    
    # Split into bins and calculate the mean of each bin
    splits = np.array_split(vals, num_bins)
    binned = np.array([np.mean(s) for s in splits if len(s) > 0])
    
    # Normalize between 0 and 7
    vmin, vmax = np.min(binned), np.max(binned)
    if vmin == vmax:
        return "▄" * len(binned)
    
    normalized = np.round((binned - vmin) / (vmax - vmin) * 7).astype(int)
    chars = ['_', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    return "".join([chars[i] for i in normalized])

def main():
    epilog_text = """
Ready-to-use Examples (just change <PROJECT_ID>):

1. Compare GKE CPU vs Memory for the last 3 hours:
   ./export_timeseries_to_csv.py -p <PROJECT_ID> --from "3 hours ago" \\
     -m "kubernetes.io/container/cpu/core_usage_time,kubernetes.io/container/memory/used_bytes" \\
     -o gke_cpu_mem.csv

2. Compare Cloud Run Request Count vs Latency for the last hour:
   ./export_timeseries_to_csv.py -p <PROJECT_ID> --from "1 hour ago" \\
     -m "run.googleapis.com/request_count,run.googleapis.com/request_latencies" \\
     -o cloudrun_traffic.csv

3. Compare Network I/O (Received vs Sent bytes) for the last 6 hours:
   ./export_timeseries_to_csv.py -p <PROJECT_ID> --from "6 hours ago" \\
     -m "compute.googleapis.com/instance/network/received_bytes_count,compute.googleapis.com/instance/network/sent_bytes_count" \\
     -o network_io.csv
"""
    arg_parser = argparse.ArgumentParser(
        description="Pull Cloud Monitoring data to CSV with metadata and stats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_text
    )
    arg_parser.add_argument("--project", "-p", required=True, help="Google Cloud Project ID")
    arg_parser.add_argument("--metric_names", "-m", required=True, help="Comma-separated metric type(s) to query.")
    arg_parser.add_argument("--filter", "-f", help="Additional filter string to append to the query (e.g., 'resource.labels.pod_name = starts_with(\"frontend-\")').")
    arg_parser.add_argument("--output", "-o", default="output.csv", help="Output CSV filename")
    arg_parser.add_argument("--from_time", "--from", dest="start_time", help="Start time (ISO8601 or 'X hours ago'). Defaults to 1 hour ago.")
    arg_parser.add_argument("--to_time", "--to", dest="end_time", help="End time (ISO8601). Defaults to now.")
    arg_parser.add_argument("--align_seconds", type=int, help="Bucket size in seconds for data aggregation (e.g., 3600 for 1 hour). If omitted, fetches raw data.")
    arg_parser.add_argument("--aligner", default="ALIGN_MEAN", help="How to aggregate data in the bucket (e.g., ALIGN_MEAN, ALIGN_MAX, ALIGN_SUM, ALIGN_RATE, ALIGN_PERCENTILE_99). Defaults to ALIGN_MEAN.")
    arg_parser.add_argument("--num_bins", type=int, default=16, help="Number of bins (characters) for the sparkline shape. Defaults to 16.")
    
    if len(sys.argv) == 1:
        arg_parser.print_help()
        sys.exit(1)

    args = arg_parser.parse_args()
    
    # Process comma-separated metric names
    metric_names_list = [m.strip() for m in args.metric_names.split(",") if m.strip()]

    # Determine time window
    now = datetime.now(timezone.utc)
    end_time = parse_time(args.end_time, now)
    start_time = parse_time(args.start_time, end_time - timedelta(hours=1))

    # Build the Monitoring client
    try:
        credentials, project = google.auth.default()
        client = monitoring_v3.MetricServiceClient(credentials=credentials)
    except Exception as e:
        print(f"Failed to authenticate with GCP: {e}", file=sys.stderr)
        sys.exit(1)

    project_name = f"projects/{args.project}"
    
    # Prepare the time interval
    interval = monitoring_v3.TimeInterval(
        {
            "end_time": end_time,
            "start_time": start_time,
        }
    )

    # Prepare optional aggregation
    aggregation = None
    if args.align_seconds:
        try:
            aligner_enum = getattr(monitoring_v3.Aggregation.Aligner, args.aligner.upper())
        except AttributeError:
            print(f"Warning: Invalid aligner '{args.aligner}'. Falling back to ALIGN_MEAN.", file=sys.stderr)
            aligner_enum = monitoring_v3.Aggregation.Aligner.ALIGN_MEAN

        aggregation = monitoring_v3.Aggregation(
            {
                "alignment_period": {"seconds": args.align_seconds},
                "per_series_aligner": aligner_enum,
            }
        )

    all_data_points = []
    label_keys = set()
    stats_summary = {}
    
    for metric_name in metric_names_list:
        filter_str = f'metric.type = "{metric_name}"'
        if args.filter:
            filter_str += f" AND {args.filter}"
        print(f"Querying {metric_name} with filter: {filter_str}", file=sys.stderr)
        print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}...", file=sys.stderr)
        
        request_params = {
            "name": project_name,
            "filter": filter_str,
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
        if aggregation:
            request_params["aggregation"] = aggregation

        try:
            results = client.list_time_series(request=request_params)
        except Exception as e:
            print(f"Error querying Cloud Monitoring API for {metric_name}: {e}", file=sys.stderr)
            continue

        metric_values = []
        metric_points = []

        # Process results
        for series in results:
            # Extract resource and metric labels
            labels = {}
            if series.resource and series.resource.labels:
                for k, v in series.resource.labels.items():
                    labels[f"resource_{k}"] = v
                    label_keys.add(f"resource_{k}")
            if series.metric and series.metric.labels:
                for k, v in series.metric.labels.items():
                    labels[f"metric_{k}"] = v
                    label_keys.add(f"metric_{k}")
                    
            for point in series.points:
                # Value extraction
                val = None
                if "int64_value" in point.value:
                    val = point.value.int64_value
                elif "double_value" in point.value:
                    val = point.value.double_value
                elif "bool_value" in point.value:
                    val = point.value.bool_value
                elif "string_value" in point.value:
                    val = point.value.string_value
                elif "distribution_value" in point.value:
                    val = point.value.distribution_value.mean # simplify dist to mean
                    
                if val is not None:
                    ts = point.interval.start_time
                    pt_dict = {
                        "timestamp": ts.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "metric_name": metric_name,
                        "value": val
                    }
                    pt_dict.update(labels)
                    metric_points.append(pt_dict)
                    metric_values.append(val)

        if metric_points:
            # Sort metric points chronologically first
            metric_points.sort(key=lambda x: x["timestamp"])
            all_data_points.extend(metric_points)
            
            # Extract values in chronological order
            vals = np.array([pt["value"] for pt in metric_points])
            min_idx = np.argmin(vals)
            max_idx = np.argmax(vals)
            
            stats_summary[metric_name] = {
                "count": len(vals),
                "shape": generate_sparkline(vals, num_bins=args.num_bins),
                "min": vals[min_idx],
                "min_ts": metric_points[min_idx]["timestamp"],
                "min_pos": get_position_label(min_idx, len(vals)),
                "max": vals[max_idx],
                "max_ts": metric_points[max_idx]["timestamp"],
                "max_pos": get_position_label(max_idx, len(vals)),
                "avg": np.mean(vals),
                "var": np.var(vals)
            }

    # Sort all data by timestamp for the CSV
    all_data_points.sort(key=lambda x: x["timestamp"])

    label_keys = sorted(list(label_keys))
    headers = ["timestamp", "metric_name", "value"] + label_keys

    print(f"Writing {len(all_data_points)} data points to {args.output}...", file=sys.stderr)

    with open(args.output, 'w', newline='') as csvfile:
        # Write metadata headers
        csvfile.write(f"# metadata_filename: {os.path.basename(args.output)}\n")
        csvfile.write(f"# metadata_metric_names: {', '.join(metric_names_list)}\n")
        csvfile.write(f"# metadata_from_timestamp: {start_time.isoformat()}\n")
        csvfile.write(f"# metadata_to_timestamp: {end_time.isoformat()}\n")
        
        # Display and write stats
        print("\n" + "="*40)
        print("DESCRIPTIVE STATISTICS")
        print("="*40)
        for m, s in stats_summary.items():
            # Extract just HH:MM:SS from 'YYYY-MM-DDTHH:MM:SS.fZ'
            min_time = s['min_ts'][11:19]
            max_time = s['max_ts'][11:19]
            
            print(f"\nMetric: {m}")
            print(f"  Shape:    {s['shape']}")
            print(f"  Count:    {s['count']}")
            print(f"  Average:  {s['avg']:.4f}")
            print(f"  Variance: {s['var']:.4f}")
            print(f"  Minimum:  [{min_time}] {s['min']:.4f} ({s['min_pos']})")
            print(f"  Maximum:  [{max_time}] {s['max']:.4f} ({s['max_pos']})")
            
            # Write to CSV header
            csvfile.write(f"# stats_{m}_shape: {s['shape']}\n")
            csvfile.write(f"# stats_{m}_avg: {s['avg']}\n")
            csvfile.write(f"# stats_{m}_min: [{min_time}] {s['min']} ({s['min_pos']})\n")
            csvfile.write(f"# stats_{m}_max: [{max_time}] {s['max']} ({s['max_pos']})\n")

        # Synoptic Comparison for multiple metrics
        if len(stats_summary) > 1:
            print("\n" + "="*40)
            print("SYNOPTIC COMPARISON")
            print("="*40)
            for m, s in stats_summary.items():
                print(f"{s['shape']}  {m}")
            print("="*40)

        csvfile.write(f"# metadata_point_count: {len(all_data_points)}\n")
        
        # Write CSV data
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_data_points)

    print(f"\nDone. Exported {len(all_data_points)} points to {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
