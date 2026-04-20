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
# requires-python = ">=3.10"
# dependencies = [
#     "pandas",
#     "numpy",
#     "python-dateutil"
# ]
# ///

import argparse
import sys
import numpy as np
import pandas as pd

def generate_sparkline(vals, num_bins=16, wrapper="|"):
    """
    Generates an ASCII sparkline from a sequence of values.
    Uses ' ' (space) for the lowest/empty bucket to ensure empty spots are visible when framed.
    """
    if len(vals) == 0:
        return f"{wrapper}{wrapper}"
    if len(vals) < num_bins:
        num_bins = len(vals)
        
    splits = np.array_split(vals, num_bins)
    binned = np.array([np.mean(s) for s in splits if len(s) > 0])
    
    vmin, vmax = np.min(binned), np.max(binned)
    if vmin == vmax:
        shape_str = "▄" * len(binned)
        return f"{wrapper}{shape_str}{wrapper}"
        
    normalized = np.round((binned - vmin) / (vmax - vmin) * 7).astype(int)
    # Replaced lowest char '_' with ' ' (space) as requested for better framing visibility
    chars = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    shape_str = "".join([chars[i] for i in normalized])
    return f"{wrapper}{shape_str}{wrapper}"

def main():
    parser = argparse.ArgumentParser(description="Generates an ASCII sparkline from a CSV file.")
    parser.add_argument("--csv", required=True, help="Path to the input CSV data")
    parser.add_argument("--values-column-name", dest="values_column", required=True, help="Column name containing the numeric values.")
    parser.add_argument("--time-column-name", dest="time_column", required=False, help="(Optional) Time column name. Will try to auto-infer if not provided.")
    parser.add_argument("--bins", type=int, default=16, help="Number of bins (characters) in the sparkline.")
    parser.add_argument("--wrapper", type=str, default="|", help="Wrapper character around the sparkline (default: |).")
    args = parser.parse_args()

    try:
        df = pd.read_csv(args.csv)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    if args.values_column not in df.columns:
        print(f"Error: Column '{args.values_column}' not found in CSV. Available columns: {', '.join(df.columns)}", file=sys.stderr)
        sys.exit(1)

    # Autoinfer time column if not provided
    time_col = args.time_column
    if not time_col:
        # Check heuristics for time column
        time_keywords = ['time', 'timestamp', 'date', 'datetime']
        for col in df.columns:
            if any(k in col.lower() for k in time_keywords):
                time_col = col
                break
        
        # If still not found, try to see if the first column can be parsed as datetime, or just use the first column
        if not time_col and len(df.columns) > 0:
            potential_col = df.columns[0]
            if potential_col != args.values_column:
                try:
                    pd.to_datetime(df[potential_col][:5])
                    time_col = potential_col
                except:
                    # just pick the first column if no time column is found, as long as it's not the value!
                    time_col = potential_col

    if time_col and time_col in df.columns:
        try:
            # Sort by the inferred or explicit time column
            df[time_col] = pd.to_datetime(df[time_col])
            df = df.sort_values(by=time_col)
        except Exception:
            pass # ignore sorting if it's not actually a time parsing compatible column

    values = df[args.values_column].dropna().values
    if len(values) == 0:
        print(f"Error: No valid numeric data found in column '{args.values_column}'.", file=sys.stderr)
        sys.exit(1)

    sparkline = generate_sparkline(values, num_bins=args.bins, wrapper=args.wrapper)
    print(sparkline)

if __name__ == "__main__":
    main()
