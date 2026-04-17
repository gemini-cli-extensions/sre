# Changelog: Cloud Monitoring Skill

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.16] - 2026-04-16
### Added
- Rephrased gist the 'graphical' part.

## [0.2.15] - 2026-04-15
### Added
- Created `scripts/setup-frontend-slo.sh`, an automated script to deploy a Log-based Service Level Objective (99.9% availability) on an Autopilot GKE cluster.
- Created `scripts/README.md` to document the purpose and usage of the SLO setup script.
- Updated `SKILL.md` to officially list the SLO script as an available skill tool.
### Changed
- **SubAgent Delegation**: Updated `SKILL.md` to recommend delegating monitoring data extraction to SubAgents to prevent main session context bloat.
- **Mandatory Stats Reporting**: Instructed agents to always surface important statistics (AVG, MAX, MIN) and Unicode sparklines using `export_timeseries_to_csv.py`.
- **Insight Reporting**: Mandated that SubAgents report stats and any interesting insights back to the main agent.

## [0.2.14] - 2026-04-08
### Added
- Added the `--num_bins` CLI argument to `export_timeseries_to_csv.py`, allowing users to dynamically control the width (resolution) of the ASCII sparkline. Defaults to 16.

## [0.2.13] - 2026-04-08
### Changed
- Increased the sparkline `num_bins` to `16` (a clean power of 2) to provide a slightly more detailed visual shape than the compact 10-character size.
- Refreshed `references/descriptive_stats_sample.txt` to showcase the new 16-character length alongside the underscore (`_`) baseline.

## [0.2.12] - 2026-04-08
### Changed
- Refined the Unicode Sparkline generator in `export_timeseries_to_csv.py`:
  - The lowest values (zeros or minimums) are now explicitly represented by an underscore (`_`) instead of an invisible space. This ensures the baseline is always visible and the string length is deterministic even if metrics fall to absolute zero at the ends.
  - Adjusted `num_bins` down from 15 to exactly `10` characters to ensure a tighter, more predictable CLI footprint.
- Updated `references/descriptive_stats_sample.txt` to showcase the new `_`-based baseline and 10-character size.

## [0.2.11] - 2026-04-08
### Added
- Added a "Synoptic Comparison" view at the end of the statistics block in `export_timeseries_to_csv.py`. This view stacks metric shapes (sparklines) vertically for instant visual correlation.

## [0.2.10] - 2026-04-08
### Added
- Created `references/descriptive_stats_sample.txt` to provide agents with a concrete example of the CLI's terminal output, specifically showcasing the descriptive statistics block, sparklines, and percentage-based temporal labels.

## [0.2.9] - 2026-04-08
### Added
- Enhanced the `MIDDLE` position label for Min/Max statistics in `export_timeseries_to_csv.py` to include the exact percentage through the timeframe (e.g., `MIDDLE, 78.9%`) for better temporal context during investigations.

## [0.2.8] - 2026-04-08
### Fixed
- Fixed a bug where `np.argmin`/`np.argmax` computed the Minimum/Maximum timestamps based on arbitrarily ordered API responses rather than chronologically sorted data, causing sparkline trends to contradict the MIN/MAX positional labels (START/END/MIDDLE). 
- Reformatted the descriptive statistics output: timestamps now drop the Date & Timezone string, displaying simply as `[HH:MM:SS]` placed immediately before the numerical value to improve vertical alignment and readability.

## [0.2.7] - 2026-04-08
### Fixed
- Fixed an issue where the `# metadata_metric_names` CSV header generated a character-split string instead of the proper metric list after the comma-separated argument change.
- Rebuilt `sample_output_dual_metrics.csv` to correctly demonstrate interleaved, multi-metric CSV output.

## [0.2.6] - 2026-04-08
### Added
- Integrated an ultra-fast (`O(N)`, <1ms latency) Unicode Sparkline generator (` ▂▃▄▅▆▇█`) directly into `export_timeseries_to_csv.py`.
- Instantly visualizes the trend (shape) of the time-series in the terminal output and inside the exported CSV metadata.

## [0.2.5] - 2026-04-08
### Added
- Added API Aggregation control to `export_timeseries_to_csv.py` via `--align_seconds` and `--aligner` arguments. Users can now natively request data grouped into specific time buckets (e.g., 1 per hour) directly at the Cloud API layer rather than downloading raw high-frequency data.

## [0.2.4] - 2026-04-08
### Changed
- Changed `--metric_names` argument to accept a single comma-separated string (e.g., `-m metric1,metric2`) instead of space-separated arguments to avoid shell parsing ambiguity.
- Updated `--help` examples to reflect the new comma-separated syntax.

## [0.2.3] - 2026-04-08
### Added
- Added `RawDescriptionHelpFormatter` to `export_timeseries_to_csv.py` to support multi-line `epilog` blocks in `--help`.
- Included ready-to-copy-paste CLI examples directly in the `--help` output for immediate usage without needing to consult the `SKILL.md`.

## [0.2.2] - 2026-04-08
### Added
- `export_timeseries_to_csv.py` now calculates and displays descriptive statistics (Min, Max, Avg, Variance, Count) for each metric.
- Statistics include specific timestamps for Min/Max values and their relative position (START, END, MIDDLE) in the timeframe.
- Statistics are also embedded as comments in the exported CSV header for persistent reference.

## [0.2.1] - 2026-04-08
### Added
- Added a strong PREREQUISITE warning in `SKILL.md` to assert that the `google-monitoring` MCP server is installed and active before proceeding.

## [0.2.0] - 2026-04-08
### Added
- Added allowlisted MCP tools for Google Cloud Monitoring directly in the SKILL.md frontmatter.
- Updated `export_timeseries_to_csv.py` to support querying multiple metrics simultaneously (`--metric_names`).
- Added guidance in `SKILL.md` for apples-to-apples metric comparisons (e.g., Request/Response Latencies, Network RX/TX, GKE CPU/Memory).

## [0.1.0] - 2026-04-08
### Added
- Initial setup of the `cloud_monitoring` skill.
- Added `SKILL.md` with guidelines on avoiding context bloat by utilizing CSV-based data extraction.
- Added `export_timeseries_to_csv.py` (formerly `pull_data_csv.py`) to extract time-series data with metadata headers.
