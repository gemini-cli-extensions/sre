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
from sklearn.ensemble import IsolationForest

def detect_anomalies_isoforest(data_json, contamination):
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
        values = np.array([item[1] for item in timeseries]).reshape(-1, 1)
    except IndexError:
        print(json.dumps({"error": "Malformed timeseries data"}), file=sys.stderr)
        sys.exit(1)

    if len(values) == 0:
        print(json.dumps({"error": "No data points to process"}), file=sys.stderr)
        sys.exit(1)

    try:
        model = IsolationForest(contamination=contamination, random_state=42)
        anomalies = model.fit_predict(values)
        # Isolation Forest returns 1 for inliers, -1 for outliers
    except Exception as e:
        print(json.dumps({"error": f"Error during Isolation Forest detection: {e}"}), file=sys.stderr)
        sys.exit(1)

    # Add anomaly flag to the original timeseries data
    final_timeseries = []
    for i, item in enumerate(timeseries):
        final_timeseries.append(item + [True if anomalies[i] == -1 else False])

    data["columns"].append("is_anomaly")
    data["timeseries"] = final_timeseries
    data["metadata"]["detection_method"] = "isolation_forest"
    data["metadata"]["isoforest_contamination"] = contamination

    print(json.dumps(data))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detect anomalies using Isolation Forest.')
    parser.add_argument('input_file', help='Input JSON file path with timestamp and value columns')
    parser.add_argument('--contamination', type=str, default='auto', help='Contamination factor for Isolation Forest (e.g., 0.1 or "auto")')
    args = parser.parse_args()

    cont = args.contamination
    if cont != 'auto':
        try:
            cont = float(cont)
        except ValueError:
            print(json.dumps({"error": "Contamination must be a float or 'auto'"}), file=sys.stderr)
            sys.exit(1)

    try:
        with open(args.input_file, 'r') as f:
            input_json = f.read()
    except FileNotFoundError:
        print(json.dumps({"error": f"Input file not found: {args.input_file}"}), file=sys.stderr)
        sys.exit(1)

    detect_anomalies_isoforest(input_json, cont)
