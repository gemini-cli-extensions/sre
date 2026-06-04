# GCP Architecture Discovery - Schema Reference

## Storage Location

The skill uses a standard, tool-agnostic physical file directory in the workspace broken down by GCP Project and Cloud Product:

**Base Path**: `{WORKSPACE_ROOT}/GCP/{PROJECT_ID}/{CLOUD_PRODUCT}/`

Within each directory, two files must exist:
1. **`state.json`**: Structured data regarding components and references.
2. **`architecture.md`**: Human-readable topological documentation with Mermaid.js graphs.

### Initializing a Discovery Folder

```bash
# Example for a specific project and product
mkdir -p GCP/my-project/cloud_run

# Always ensure the GCP directory is gitignored if considered sensitive
echo "GCP/" >> .gitignore
```

## Cache File Structure: `state.json`

The JSON state tracks instances and references between infrastructure components.

```json
{
  "product": "cloud_run",
  "project_id": "my-project",
  "last_updated": "2026-06-02T15:00:00Z",
  "instances": [
    {
      "name": "frontend",
      "region": "us-central1",
      "discovered_at": "2026-06-02T14:30:00Z"
    }
  ],
  "references": {
    "frontend": [
      {
        "type": "cloud_sql",
        "target_project": "my-project",
        "target_name": "postgres-db"
      }
    ]
  }
}
```

### Discovery Timestamps

Each instance has a `discovered_at` timestamp indicating when it was last verified.
**Freshness Guidelines**:
- < 1 hour: Fresh, use cache
- 1-24 hours: Generally fresh, use cache unless investigating infra changes
- 1-7 days: Potentially stale, refresh if resource is affected in incident
- > 7 days: Stale, refresh before using

## Documentation: `architecture.md`

`architecture.md` should contain explanatory text outlining the relationships derived from `state.json`.

```markdown
# Architecture: my-project - cloud_run

## Overview
Briefly describe the role of cloud_run components in `my-project`.

## Mermaid Topology
\`\`\`mermaid
graph TD
    Service[frontend] --> DB[(postgres-db)]
\`\`\`
```

When discovering new resources, **merge** to existing JSON and update the Markdown descriptions accordingly.

### Cache Invalidation

**When to clear cache/re-generate documentation**:
- Major infrastructure changes (migrations, refactors)
- Documentation drift detected
- Starting fresh baseline

**How to clear**:
```bash
rm -rf GCP/
```

### Best Practices

1. **Check cache first**: Always read `state.json` and `architecture.md` before discovering
2. **Update incrementally**: Merge new data, preserve existing
3. **Respect timestamps**: Use freshness to decide when to refresh
4. **Dependency mapping**: Always update dependency graph when discovering services
5. **Team sharing**: Commit the GCP folder to git (if not sensitive) for knowledge sharing

## Query Patterns

### Find a specific service across products
```bash
find GCP/my-project/ -name "state.json" | xargs jq '.instances[] | select(.name=="frontend")'
```

### List cross-product dependencies of a service
```bash
find GCP/my-project/ -name "state.json" | xargs jq '.references.frontend'
```

