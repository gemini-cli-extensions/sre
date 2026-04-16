# 📝 Changelog: monitoring-graphs

All notable changes to the `monitoring-graphs` skill will be documented in this file.

## [0.0.5] - 2026-04-07
### 📊 The "Data Integrity & Aesthetics" Update

This version focuses on rigorous data handling during outages and improved visual storytelling for post-mortems.

#### ✨ New Features & Patterns
- 🚫 **Data Integrity Mandate:** Added strict rules against faking or hardcoding data points to fit a narrative. The raw metrics are the single source of truth.
- 🐍 **Juicy Python Patterns:** Added a highly condensed section in `SKILL.md` detailing how to reindex missing data, smooth signals, and create dual-axis plots.
- 📄 **Reference Script:** Added a fully runnable reference script (`scripts/reference_dual_plot.py`) with inline `uv run` dependencies, demonstrating the end-to-end flow of parsing MCP JSON, cleaning data, and plotting.
- 🎨 **Semantic Annotation Colors:** Standardized vertical annotation lines:
  - **Red:** Breakages/Outages (with varying thickness/style for severity).
  - **Yellow:** Human Detection.
  - **Green:** Fix/Mitigation applied.

## [0.0.1] - 2026-03-31
### 🏁 Initial Release: "Apple-to-Apple" & Rollout Edition 🕵️‍♀️🌈

This version introduces the foundation for professional SRE incident visualization on GKE and Cloud Run.

#### ✨ New Features
- 📈 **Stacked Area Charts:** Added `--stacked` flag to `plot_archetype.py` for beautiful Blue/Green rollout visualizations.
- 🎨 **Apple-to-Apple Coloring:** Automatic color coding for Network I/O (Ingress = Blue, Egress = Green) and Version transitions.
- 📏 **Scaling Limits:** Support for `--hmin` and `--hmax` horizontal lines to show Cloud Run/GKE `min_instances` and `max_instances`.
- 🌍 **UTC Standard:** All timestamps now default to UTC for global consistency, with explicit labeling on the X-axis.
- 🚀 **`uv run` Integration:** Added `#!/usr/bin/env uv run` shebang for seamless execution with managed dependencies.

#### 🕵️‍♀️ Expert Guidance
- 🔍 **Discovery vs. Refinement:** New granularity strategy (1h/1d for fast discovery, 1m/5m for post-mortems).
- 🏛️ **Metric Archetypes:** Documented strategies for Compute (Scaling), Network (I/O), and Progressive Rollouts (pod_template_hash).
- 🐢 **Performance Tips:** Built-in warnings and strategies for slow Cloud Monitoring downloads.

#### 🏗️ Architecture & Internal
- 📁 Modular structure with `scripts/` and `references/` directories.
- ✅ Two-stage workflow (Draft verification before Final annotation).
