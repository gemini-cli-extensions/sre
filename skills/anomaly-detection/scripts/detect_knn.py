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
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
import argparse

def detect_anomalies_knn(data_json, n_neighbors):
    try:
        data = json.loads(data_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}), file=sys.stderr)
        sys.exit(1)

    timeseries = data.get("timeseries")
    if not timeseries:
        print(json.dumps({"error": "'timeseries' key not found in JSON input"}), file=sys.stderr)
        sys.exit(1)

    try:
        # Extract just the values for anomaly detection
        values = np.array([item[1] for item in timeseries]).reshape(-1, 1)
    except (IndexError, TypeError) as e:
        print(json.dumps({"error": f"Error processing timeseries data: {e}"}), file=sys.stderr)
        sys.exit(1)

    if len(values) < n_neighbors:
        print(json.dumps({"error": f"Not enough data points ({len(values)}) for KNN with n_neighbors={n_neighbors}"}), file=sys.stderr)
        sys.exit(1)

    try:
        lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination='auto')
        anomalies = lof.fit_predict(values)
        # LOF returns 1 for inliers, -1 for outliers
    except Exception as e:
        print(json.dumps({"error": f"Error during KNN detection: {e}"}), file=sys.stderr)
        sys.exit(1)

    # Add anomaly flag to the original timeseries data
    for i, item in enumerate(timeseries):
        item.append(True if anomalies[i] == -1 else False)

    data["columns"].append("is_anomaly")
    data["timeseries"] = timeseries

    print(json.dumps(data))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detect anomalies using KNN Local Outlier Factor.')
    parser.add_argument('input_file', type=str, help='Input JSON file path.')
    parser.add_argument('--n_neighbors', type=int, default=20, help='Number of neighbors for LOF.')
    args = parser.parse_args()

    input_json = None
    try:
        with open(args.input_file, 'r') as f:
            input_json = f.read()
    except FileNotFoundError:
        print(json.dumps({"error": f"Input file not found: {args.input_file}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Error reading input file: {e}"}), file=sys.stderr)
        sys.exit(1)

    if not input_json:
        print(json.dumps({"error": "No input data received"}), file=sys.stderr)
        sys.exit(1)

    detect_anomalies_knn(input_json, args.n_neighbors)
