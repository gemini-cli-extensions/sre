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
import argparse
import numpy as np
import pandas as pd

def smooth_moving_average(series, window):
    return series.rolling(window=window, min_periods=1).mean()

def smooth_exponential(series, alpha):
    return series.ewm(alpha=alpha, adjust=False).mean()

def preprocess_data(data_json, smoothing_method=None, window=None, alpha=None):
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}), file=sys.stderr)
        sys.exit(1)

    metric_name = data.get("metadata", {}).get("metric_name")
    if not metric_name:
        print(json.dumps({"error": "'metadata.metric_name' key not found"}), file=sys.stderr)
        sys.exit(1)

    if data.get("columns") != ["timestamp", "value"]:
        print(json.dumps({"error": "Expected columns ['timestamp', 'value']"}), file=sys.stderr)
        sys.exit(1)

    timeseries = data.get("timeseries")
    if not timeseries:
        print(json.dumps({"error": "'timeseries' key not found"}), file=sys.stderr)
        sys.exit(1)

    try:
        timestamps = [item[0] for item in timeseries]
        values = [item[1] for item in timeseries]
    except IndexError as e:
        print(json.dumps({"error": f"Error extracting data for metric '{metric_name}': {e}"}), file=sys.stderr)
        sys.exit(1)

    # Convert to Pandas Series for smoothing
    df = pd.DataFrame({'timestamp': pd.to_datetime(timestamps), 'value': values})
    df = df.set_index('timestamp').sort_index()

    series = df['value'].astype(float) # Ensure numeric type

    if smoothing_method == "moving_average":
        if not window or window <= 0:
            print(json.dumps({"error": "Window size for moving average must be a positive integer"}), file=sys.stderr)
            sys.exit(1)
        series = smooth_moving_average(series, window)
    elif smoothing_method == "exponential":
        if not alpha or not (0 < alpha <= 1):
            print(json.dumps({"error": "Alpha for exponential smoothing must be between 0 and 1"}), file=sys.stderr)
            sys.exit(1)
        series = smooth_exponential(series, alpha)

    processed_timeseries = [[ts.isoformat(), val] for ts, val in series.items()]

    output = {
        "metadata": {
            "source_type": data["metadata"].get("source_type"),
            "source_details": data["metadata"].get("source_details"),
            "metric_name": metric_name,
            "preprocessing": {
                "method": smoothing_method,
                "window": window,
                "alpha": alpha
            }
        },
        "columns": ["timestamp", "value"],
        "timeseries": processed_timeseries
    }
    print(json.dumps(output))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocess time series data, including smoothing.')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('--smoothing_method', choices=['moving_average', 'exponential'], help='Smoothing method to apply')
    parser.add_argument('--window', type=int, help='Window size for Moving Average')
    parser.add_argument('--alpha', type=float, help='Alpha value for Exponential Smoothing')
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            input_json = f.read()
    except FileNotFoundError:
        print(json.dumps({"error": f"Input file not found: {args.input_file}"}), file=sys.stderr)
        sys.exit(1)

    preprocess_data(input_json, args.smoothing_method, args.window, args.alpha)
