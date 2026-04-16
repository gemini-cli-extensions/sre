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

import csv
import json
import sys
import os
from datetime import datetime

def parse_csv_to_standard_json(file_path):
    if not os.path.exists(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(1)

    timeseries = []
    metric_name = "value"
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            if len(header) != 2:
                print(json.dumps({"error": "CSV must have exactly two columns: timestamp and value"}), file=sys.stderr)
                sys.exit(1)
            if header[0].lower() != 'timestamp':
                print(json.dumps({"error": "First column must be named 'timestamp'"}), file=sys.stderr)
                sys.exit(1)
            metric_name = header[1]

            for row in reader:
                if len(row) != 2:
                    print(json.dumps({"error": f"Row format error in CSV: {row}"}), file=sys.stderr)
                    continue
                try:
                    timestamp = datetime.fromisoformat(row[0]).isoformat() + "Z"
                    value = float(row[1])
                    timeseries.append([timestamp, value])
                except ValueError as e:
                    print(json.dumps({"error": f"Data conversion error in row {row}: {e}"}), file=sys.stderr)
                    continue
    except Exception as e:
        print(json.dumps({"error": f"Error reading CSV file {file_path}: {e}"}), file=sys.stderr)
        sys.exit(1)

    standardized_output = {
        "metadata": {
            "source_type": "csv",
            "source_details": file_path,
            "metric_name": metric_name
        },
        "columns": ["timestamp", metric_name],
        "timeseries": timeseries
    }
    print(json.dumps(standardized_output))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python parse_csv.py <file_path>"}), file=sys.stderr)
        sys.exit(1)
    parse_csv_to_standard_json(sys.argv[1])
