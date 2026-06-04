# Changelog - GCP Architecture Discovery

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-31

### Added
- **Incremental discovery** approach instead of bulk scanning
- **State management** using VS Code memory system:
  - Repository memory for long-term architecture cache per project
  - Session memory for tracking current investigation discoveries
  - Local JSON cache as optional fallback
- **Targeted discovery commands** for single resource lookup
- **Cache management** with merge, refresh, and invalidation strategies
- Comprehensive discovery workflows for:
  - Compute resources (GCE, GKE, Cloud Run, Cloud Functions, App Engine)
  - Networking components (VPC, load balancers, DNS, firewall rules)
  - Storage resources (Cloud Storage, Cloud SQL, persistent disks)
  - Service dependencies (service accounts, IAM, APIs)
  - Monitoring and logging setup
- **Incident-driven discovery pattern**: start from alert → discover affected service → expand to dependencies
- Investigation checklist optimized for incremental approach
- Common architecture patterns documentation
- Safe mode support for read-only operations
- Integration points with related skills (gcp-setup, gcp-playbooks, cloud-monitoring)

### Documentation
- Core incremental discovery workflow with cache-first approach
- Targeted vs bulk discovery command distinction
- gcloud command examples for single-resource discovery (preferred)
- kubectl commands for GKE discovery
- Cache structure and management procedures
- Session discovery logging template
- Architecture diagramming recommendations
- Troubleshooting guide including cache staleness and refresh procedures

### References
- `cache-structure-example.json`: Complete example of cache structure with dependencies
- `README.md`: Detailed documentation of cache management, query patterns, and best practices

### Philosophy
- "Discover what you need, when you need it" vs scanning everything
- Cache results for reuse across investigations
- Faster investigation startup times
- Reduced API calls and quota consumption
