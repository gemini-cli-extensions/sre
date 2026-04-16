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
#     "matplotlib"
# ]
# ///

import json
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# Reference: This script shows the pattern for parsing Monitoring JSON,
# cleaning up the timeline with Pandas, and plotting a Dual Axis graph.

def generate_graph(json_file, output_file='incident_graph.png'):
    with open(json_file) as f:
        data = json.load(f)

    records = []
    for ts in data.get('timeSeries', []):
        metric_labels = ts['metric']['labels']
        code = metric_labels.get('response_code', 'unknown')
        
        for p in ts.get('points', []):
            et = pd.to_datetime(p['interval']['endTime'])
            st = pd.to_datetime(p['interval']['startTime'])
            
            # Filter for 1-minute delta points only (standard GKE/Istio metric behavior)
            if (et - st).total_seconds() > 120: continue
                
            val = int(p['value'].get('int64Value', 0))
            records.append({'Time': et, 'Code': code, 'Val': val})

    if not records:
        print("NO DATA FOUND!")
        return

    df = pd.DataFrame(records)
    # Ensure time is in a usable TZ-aware or TZ-naive format consistent with the data
    df['Time'] = df['Time'].dt.tz_convert('UTC') 
    df['IsSuccess'] = df['Code'].str.startswith('2')

    # 1. Handling Missing Data (Reindexing)
    # Force a continuous time index from the start to end of the data found
    full_range = pd.date_range(start=df['Time'].min(), end=df['Time'].max(), freq='1min')
    
    # Group, pivot success/fail, and reindex to fill blackout gaps with 0s
    grouped = df.groupby([pd.Grouper(key='Time', freq='1min'), 'IsSuccess'])['Val'].sum().unstack(fill_value=0)
    grouped = grouped.reindex(full_range, fill_value=0)

    # Ensure True/False columns exist even if all traffic failed or all succeeded
    for col in [True, False]:
        if col not in grouped.columns: grouped[col] = 0

    grouped['Total'] = grouped[True] + grouped[False]
    grouped['Availability'] = (grouped[True] / grouped['Total']) * 100
    grouped['Availability'] = grouped['Availability'].fillna(0)

    # 2. Smoothing "Golden Signals"
    volume = grouped['Total'].rolling(5, min_periods=1).mean()
    avail = grouped['Availability'].rolling(5, min_periods=1).mean()

    # 3. Dual Axes (Availability & Traffic)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)

    # TOP: Availability (%)
    ax1.plot(avail.index, avail, color='#d93025', linewidth=3, label='Availability %')
    ax1.fill_between(avail.index, avail, color='#d93025', alpha=0.1)
    ax1.set_ylabel('Success Rate (%)', fontsize=12)
    ax1.set_ylim(-5, 105)
    ax1.set_title('Incident Visualization: Availability vs Volume', fontsize=18, fontweight='bold')

    # BOTTOM: Traffic Volume (Req/min)
    ax2.plot(volume.index, volume, color='#1a73e8', linewidth=2, label='Traffic Volume')
    ax2.fill_between(volume.index, volume, color='#1a73e8', alpha=0.1)
    ax2.set_ylabel('Req / Min', fontsize=12)
    ax2.set_xlabel('Time (UTC)', fontsize=12)

    # Annotations: Breakages (Red), Detection (Yellow), Fix (Green)
    events = [
        # time, color, style, thickness, label
        (datetime(2026, 4, 7, 1, 11), '#d93025', ':', 2, 'Canary Typo (Minor)'),
        (datetime(2026, 4, 7, 2, 46), '#d93025', '-.', 3, 'Istio 503 Fault (Major)'),
        (datetime(2026, 4, 7, 11, 56), '#f9ab00', '--', 2, 'Detected'),
        (datetime(2026, 4, 7, 12, 21), '#1e8e3e', '-', 2, 'Resolved')
    ]

    for time, color, style, lw, label in events:
        for ax in [ax1, ax2]:
            ax.axvline(time, color=color, linestyle=style, linewidth=lw, label=label if ax == ax1 else "")

    ax1.grid(True, linestyle=':', alpha=0.6)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='lower left')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Reference graph saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reference_dual_plot.py <monitoring_mcp_output.json>")
    else:
        generate_graph(sys.argv[1])
