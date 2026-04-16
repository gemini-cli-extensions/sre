#!/usr/bin/env uv run
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
#     "matplotlib",
#     "pytz"
# ]
# ///

import os
import argparse
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Expert SRE Incident Graphing Archetype")
    parser.add_argument("--csv", required=True, help="Path to the input CSV data")
    parser.add_argument("--out", required=True, help="Path to the output PNG image")
    parser.add_argument("--title", default="Incident Metric Over Time", help="Title of the graph")
    parser.add_argument("--ylabel", default="Metric Value", help="Label for the Y-axis")
    parser.add_argument("--final", action="store_true", help="Generate the final graph with incident milestones")
    parser.add_argument("--stacked", action="store_true", help="Create a stacked area chart (ideal for rollouts!)")
    
    # Milestone Times
    parser.add_argument("--start", help="Incident start time (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--detect", help="Incident detection time (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--mitigate", help="Incident mitigation time (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--end", help="Incident end time (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--timezone", default="UTC", help="Timezone for the timestamps (default: UTC)")

    # Scaling Lines
    parser.add_argument("--hmin", type=float, help="Horizontal line for Minimum value")
    parser.add_argument("--hmax", type=float, help="Horizontal line for Maximum value")

    args = parser.parse_args()

    # Load Data
    if not os.path.exists(args.csv):
        print(f"❌ Error: CSV file not found: {args.csv}")
        return

    df = pd.read_csv(args.csv, index_col='time', parse_dates=True).fillna(0)
    if df.empty:
        print(f"⚠️ Warning: CSV file is empty: {args.csv}")
        return

    # Plotting
    plt.figure(figsize=(12, 6))
    
    if args.stacked:
        # Stacked Area Chart for Rollouts 🌈
        plt.stackplot(df.index, [df[col] for col in df.columns], labels=df.columns, alpha=0.8)
    else:
        # Standard Line Plot
        for column in df.columns:
            color = None
            if "ingress" in column.lower() or "v1" in column.lower(): color = "green"
            elif "egress" in column.lower() or "v2" in column.lower(): color = "blue"
            plt.plot(df.index, df[column], label=column, color=color)
        
    # Horizontal Scaling Lines
    if args.hmin is not None:
        plt.axhline(y=args.hmin, color='gray', linestyle=':', label=f'Min ({args.hmin})')
    if args.hmax is not None:
        plt.axhline(y=args.hmax, color='black', linestyle=':', label=f'Max ({args.hmax})')

    plt.title(args.title)
    plt.xlabel(f"Time ({args.timezone})")
    plt.ylabel(args.ylabel)
    plt.grid(True, alpha=0.3)
    
    if args.final:
        milestones = [
            (args.start, 'red', 'Start'),
            (args.detect, 'yellow', 'Detected'),
            (args.mitigate, 'orange', 'Mitigated'),
            (args.end, 'red', 'End')
        ]
        
        active_milestones = []
        for time_str, color, label in milestones:
            if time_str:
                try:
                    ts = pd.to_datetime(time_str)
                    if ts.tzinfo is None: ts = ts.tz_localize(args.timezone)
                    else: ts = ts.tz_convert(args.timezone)
                    plt.axvline(x=ts, color=color, linestyle='--', label=label)
                    active_milestones.append(label)
                except Exception as e:
                    print(f"⚠️ Warning: Milestone {label} failed: {e}")
        
        if active_milestones or args.hmin is not None or args.hmax is not None or args.stacked:
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
            plt.subplots_adjust(bottom=0.25)
        else:
            plt.legend()
    else:
        plt.legend()
        
    plt.savefig(args.out)
    print(f"✅ Saved graph to {args.out} (Stacked: {args.stacked})")

if __name__ == "__main__":
    main()
