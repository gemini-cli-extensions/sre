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

def detect_anomalies_zscore(data_json, threshold, rolling_window):
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}), file=sys.stderr)
        sys.exit(1)

    timeseries = data.get("timeseries")
    if not timeseries or not all(len(item) == 2 for item in timeseries):
        print(json.dumps({"error": "'timeseries' must be a list of [timestamp, value] pairs"}), file=sys.stderr)
        sys.exit(1)

    try:
        timestamps = [item[0] for item in timeseries]
        values = [item[1] for item in timeseries]
    except IndexError:
        print(json.dumps({"error": "Malformed timeseries data"}), file=sys.stderr)
        sys.exit(1)

    df = pd.DataFrame({'timestamp': pd.to_datetime(timestamps), 'value': values})
    df = df.set_index('timestamp').sort_index()
    series = df['value'].astype(float)

    if len(series) < rolling_window:
        print(json.dumps({"error": f"Not enough data points ({len(series)}) for rolling window {rolling_window}"}), file=sys.stderr)
        sys.exit(1)

    rolling_mean = series.rolling(window=rolling_window, min_periods=1).mean()
    rolling_std = series.rolling(window=rolling_window, min_periods=1).std().fillna(0)

    z_scores = np.abs((series - rolling_mean) / rolling_std.replace(0, np.nan))
    is_anomaly = z_scores > threshold

    # Add anomaly flag to the original timeseries data
    anomalies_map = {df.index[i]: is_anomaly.iloc[i] for i in range(len(df))}

    final_timeseries = []
    for item in timeseries:
        ts = pd.to_datetime(item[0])
        anomaly_flag = bool(anomalies_map.get(ts, False)) # Default to False if ts not found
        final_timeseries.append(item + [anomaly_flag])

    data["columns"].append("is_anomaly")
    data["timeseries"] = final_timeseries
    data["metadata"]["detection_method"] = "zscore"
    data["metadata"]["zscore_threshold"] = threshold
    data["metadata"]["zscore_window"] = rolling_window

    print(json.dumps(data))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detect anomalies using rolling Z-score.')
    parser.add_argument('input_file', help='Input JSON file path with timestamp and value columns')
    parser.add_argument('--threshold', type=float, default=3.0, help='Z-score threshold for anomaly detection')
    parser.add_argument('--rolling_window', type=int, default=30, help='Rolling window size for mean/std calculation')
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as f:
            input_json = f.read()
    except FileNotFoundError:
        print(json.dumps({"error": f"Input file not found: {args.input_file}"}), file=sys.stderr)
        sys.exit(1)

    detect_anomalies_zscore(input_json, args.threshold, args.rolling_window)
