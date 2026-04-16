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
from collections import defaultdict
from datetime import datetime

def merge_timeseries_data(json_file_paths):
    all_data = []
    for file_path in json_file_paths:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                all_data.append(data)
        except FileNotFoundError:
            print(json.dumps({"error": f"Input file not found: {file_path}"}), file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError:
            print(json.dumps({"error": f"Invalid JSON in file: {file_path}"}), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(json.dumps({"error": f"Error reading file {file_path}: {e}"}), file=sys.stderr)
            sys.exit(1)

    if not all_data:
        print(json.dumps({"error": "No data to merge"}), file=sys.stderr)
        sys.exit(1)

    merged_metrics = defaultdict(dict)
    all_timestamps = set()
    metric_names = []

    for data in all_data:
        metric_name = data['metadata']['metric_name']
        metric_names.append(metric_name)
        for ts_str, value in data['timeseries']:
            all_timestamps.add(ts_str)
            merged_metrics[ts_str][metric_name] = value

    sorted_timestamps = sorted(list(all_timestamps))

    final_timeseries = []
    for ts_str in sorted_timestamps:
        row = [ts_str]
        for metric in metric_names:
            row.append(merged_metrics[ts_str].get(metric, None))
        final_timeseries.append(row)

    result = {
        "metadata": {
            "source_type": "csv_merged",
            "source_details": json_file_paths,
            "available_metrics": metric_names
        },
        "columns": ["timestamp"] + metric_names,
        "timeseries": final_timeseries
    }
    print(json.dumps(result))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge multiple single-metric JSON timeseries files.')
    parser.add_argument('json_files', nargs='+', help='List of JSON file paths to merge.')
    args = parser.parse_args()
    merge_timeseries_data(args.json_files)
