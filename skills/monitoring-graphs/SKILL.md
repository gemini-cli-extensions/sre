---
name: monitoring-graphs
description: 🐉 skill for generating high-quality, annotated incident graphs for post-mortems using Python. Use this when the user needs to visualize an outage, show error rates, or correlate metrics with incident milestones.
#verbose_description: Expert SRE skill for generating high-quality, annotated incident graphs for post-mortems using Python and Monitoring MCP on Google Cloud. Use this when the user needs to visualize an outage, show error rates, or correlate metrics with incident milestones (start, detection, mitigation, end).
metadata:
  author: Riccardo Carlesso
  version: 0.0.5
---

# 📈 Monitoring & Incident Graphing Skill 📊

This skill guides the agent through identifying high-signal metrics, extracting data efficiently, and creating professional annotated graphs.

## 🚨 DATA INTEGRITY: NEVER MAKE UP NUMBERS
- **ONLY REAL DATA:** Absolutely **NEVER** fake data, interpolate guesses, or hard-code values (like forcing a firewall block period to exactly 0) just to make a graph look "correct" or align with a narrative. 
- **The Data Is The Source Of Truth:** If there is an outage, the raw metrics or the *absence* of metrics must prove it. Show the *real* raw availability.
- **Handling Complete Blackouts:** If a full blackout causes missing data points from the API, do not invent data. Instead, use Pandas `reindex` to fill the missing continuous time intervals with 0s.

## 🚀 Workflow

### 1. Metric Selection & Efficient Extraction 🕵️‍♀️
- **Standard Time:** Always use **UTC** for all timestamps by default. 🌐
- **Performance Tip:** Cloud Monitoring can be **VERY SLOW** for high-res data. 🐢
- **Execution:**
  1. Use Monitoring MCP to find relevant metrics for the incident time window.
  2. Download the data as CSV (e.g., `out/incident/metric.csv`) or directly parse JSON.
  3. Use a sub-agent (`generalist`) for large datasets to keep the main session history lean.
- **Reference:** See [archetypes.md](references/archetypes.md) for "Apple-to-Apple" strategies and granularity tables.

### 2. Baseline Graph (Draft) 🖼️
- **Rule:** Always generate a raw "Draft" graph first to confirm the data shows a clear signal.
- **Command:**
  ```bash
  uv run ./scripts/plot_archetype.py --csv data.csv --out draft.png --title "Title"
  ```
- **Verification:** Ensure the graph is not "flat." The X-axis must explicitly show "Time (UTC)" so there is no ambiguity! 🕰️

### 3. Annotated Graph (Final) 🔴
- **Requirement:** Only proceed after the user confirms the draft is "good."
- **Command:**
  ```bash
  # Times are assumed to be UTC unless --timezone is specified
  uv run ./scripts/plot_archetype.py \
    --csv data.csv \
    --out final.png \
    --final \
    --start "YYYY-MM-DD HH:MM:SS" \
    --detect "YYYY-MM-DD HH:MM:SS" \
    --mitigate "YYYY-MM-DD HH:MM:SS" \
    --end "YYYY-MM-DD HH:MM:SS"
  ```
- **Styling Guidelines (Annotations):**
  - **Red (`#d93025`):** Breakages, outages, faults, or incident start/end. Use different line thicknesses (`linewidth=1` to `3`) or styles (`:`, `--`, `-.`) to denote severity.
  - **Yellow (`#f9ab00`):** Human detection or alert triggered.
  - **Green (`#1e8e3e`):** Fix, mitigation, or resolution applied.

## 📝 Safeguards & Tips

* **Scaling Lines:** Use `--hmin` and `--hmax` to show Cloud Run/GKE scaling limits (min/max instances).
* **Auto-Coloring:** Blue for `ingress`, Green for `egress` for Network I/O.
* **Timeouts:** Use `timeout 60` for data extraction tool calls to avoid infinite loops. Also prefer MCP calls to Monitoring/Logging (faster) vs `gcloud` commands (slower).
* **Clear Timing:** Ensure that looking at the time variable allows a person to know EXACTLY what that time is. 
    * For instance, if time is 03:00 ensure the TZ is specified in the X-axis label.
    * If the graph only contains HOURS (ie, all happens within a day) and no days, then ensure the day is also written in the X-axis label.
* **Correlation in graphs**: if you need to prove a time-correlation between heterogeneous graphs (eg error logs volume vs increase in traffic) remember:
    * **Time is key** - keep a single X-axis with consistent time across the 2+ graphs.
    * Example: `assets/sample_correlation_data/improved_incident_graphs.png`
* **Revision and multiple files**. Since images are very succulent, if you create a new image do NOT overwrite the old image, rather add _rev1, _rev2, .. to the file name.
    * If an image is proven to be wrong by further investigation, do NOT delete it, rather add it to Trash/ within the original folder, and possibly rename it to why it was wrong in the filename.

## 🐍 Juicy Python Patterns (From Real Investigations)

See `scripts/reference_dual_plot.py` for a complete example of parsing JSON and plotting.

### 1. Handling Missing Data (Reindexing)
```python
# Force 0s for missing data in outages (Pandas)
full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='1min')
df = df.reindex(full_range, fill_value=0)
```

### 2. Smoothing "Golden Signals"
```python
# 5min rolling average for smoother 'Golden Signal' look
vol_smooth = grouped['Total'].rolling(5, min_periods=1).mean().fillna(0)
avail_smooth = grouped['Availability'].rolling(5, min_periods=1).mean().fillna(0)
```

### 3. Dual Axes (Availability & Traffic)
```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
ax1.plot(df.index, df.avail, color='#d93025', label='Success Rate') # Top: %
ax1.fill_between(df.index, df.avail, color='#d93025', alpha=0.1)
ax2.plot(df.index, df.vol, color='#1a73e8', label='Traffic') # Bottom: Volume
ax2.fill_between(df.index, df.vol, color='#1a73e8', alpha=0.1)
```
