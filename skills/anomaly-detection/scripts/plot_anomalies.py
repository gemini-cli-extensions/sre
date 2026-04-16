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

import json
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import tempfile
import argparse

def plot_anomalies(data_json):
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}), file=sys.stderr)
        sys.exit(1)

    timeseries = data.get("timeseries")
    if not timeseries:
        print(json.dumps({"error": "'timeseries' key not found in JSON input"}), file=sys.stderr)
        sys.exit(1)

    metadata = data.get("metadata", {})
    metric_name = metadata.get("metric_name", "Value")

    try:
        timestamps = [datetime.fromisoformat(item[0].replace('Z', '')) for item in timeseries]
        values = [item[1] for item in timeseries]
        is_anomaly = [item[2] for item in timeseries]
    except (IndexError, TypeError, ValueError) as e:
        print(json.dumps({"error": f"Error processing timeseries data for plotting: {e}"}), file=sys.stderr)
        sys.exit(1)

    anomaly_ts = [timestamps[i] for i, anomaly in enumerate(is_anomaly) if anomaly]
    anomaly_val = [values[i] for i, anomaly in enumerate(is_anomaly) if anomaly]

    try:
        plt.figure(figsize=(15, 5))
        plt.plot(timestamps, values, label='Actual Data', color='blue', linestyle='-', marker='.')
        plt.plot(anomaly_ts, anomaly_val, label='Anomaly', color='red', linestyle='None', marker='o')

        plt.xlabel("Timestamp")
        plt.ylabel(metric_name)
        plt.title(f"Anomaly Detection for {metric_name}")
        plt.legend()
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.xticks(rotation=45)
        plt.tight_layout()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False, dir="/tmp") as tmpfile:
            plot_filename = tmpfile.name
            plt.savefig(plot_filename)
            print(plot_filename)
        plt.close()
    except Exception as e:
        print(json.dumps({"error": f"Error during plotting: {e}"}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot anomalies from JSON data.')
    parser.add_argument('input_file', nargs='?', type=str, help='Optional input JSON file path. Reads from stdin if not provided.')
    args = parser.parse_args()

    if args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                input_json = f.read()
        except FileNotFoundError:
            print(json.dumps({"error": f"Input file not found: {args.input_file}"}), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": f"Error reading input file: {e}"}), file=sys.stderr)
            sys.exit(1)
    else:
        input_json = sys.stdin.read()

    if not input_json:
        print(json.dumps({"error": "No input data received"}), file=sys.stderr)
        sys.exit(1)

    plot_anomalies(input_json)
