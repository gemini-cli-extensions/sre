# Changelog

## [0.0.2] - 2026-04-13
- Changed: `gcp-whoami.sh` output cleanly handles omitting redundant duplicate `Context` paths and empty `default` namespaces.
- Changed: `gcp-whoami.sh` extracts human-friendly cluster names natively out of GKE contexts (`gke_{project}_{zone}_{cluster}`).
- Added: `gcp-whoami.sh` now reliably appends accurate `Project ID` lines underneath both `gcloud` and `ADC` identities, incorporating a multi-tier fallback parsing of `application_default_credentials.json` out of the ~/.config directories when tokens don't natively attach them.

## [0.0.1] - Initial Version
- Bootstrapped GCP Setup Skill with underlying authentication scripts.
