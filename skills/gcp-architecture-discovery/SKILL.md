---
name: gcp-architecture-discovery
description: 🐉 [SRE] Discover and map GCP infrastructure architecture including compute, networking, storage, and service dependencies. Use when investigating incidents or documenting system topology.
metadata:
  author: SRE Team
  version: 0.1.0
  status: draft
---

# GCP Architecture Discovery

## Overview

This skill provides an **incremental discovery** approach for GCP infrastructure. Instead of scanning everything at once, it discovers only what's needed for the current investigation and caches results for future use.

## When to Use

- Starting an incident investigation and need to understand affected infrastructure
- Following up on alerts - discover only the implicated resources
- Onboarding to a new GCP project (initial baseline discovery)
- Identifying dependencies between services during incidents
- Creating architecture diagrams for postmortems
- Auditing specific resource configurations

## Discovery Strategy: Incremental & Cached

### Philosophy

**Don't discover everything - discover what you need, when you need it.**

- Start from the **affected service** (from alert/incident)
- Discover **dependencies incrementally** (upstream/downstream)
- **Cache results** in repository memory for future investigations
- **Refresh selectively** when changes are suspected

### State Management

This skill uses a tool-agnostic, local file-based topology documentation approach.

The folder structure **MUST** be organized by Project and Cloud Product:
`{AGENT_WORKSPACE_ROOT}/GCP/{PROJECT_ID}/{CLOUD_PRODUCT}/`

Inside each product directory, maintain two explicit files:

1. **`state.json` (Structured Data Cache)**:
   - Contains a list of instances.
   - Contains references/dependencies to other resources.
   - Easy for the agent to parse programmatically.

2. **`architecture.md` (Topological Documentation)**:
   - Contains markdown documentation explaining how these pieces of architecture work together.
   - Includes visual graphs (e.g., Mermaid.js) representing the flow, boundaries, and dependencies.
   - Easy for humans and reasoning models to read contexturally.

### Cache Structure Examples

#### Example: `{WORKSPACE_ROOT}/GCP/my-project/cloud_run/state.json`
```json
{
  "product": "cloud_run",
  "project_id": "my-project",
  "last_updated": "2026-06-02T10:30:00Z",
  "instances": [
    {
      "name": "frontend",
      "region": "us-central1",
      "url": "https://frontend-xxx.run.app",
      "last_revision": "frontend-00042-abc",
      "discovered_at": "2026-06-02T10:15:00Z"
    }
  ],
  "references": {
    "frontend": [
      {
        "type": "cloud_sql",
        "target_project": "my-project",
        "target_name": "postgres-db"
      },
      {
        "type": "pubsub",
        "target_project": "my-project",
        "target_name": "events-topic"
      }
    ]
  }
}
```

#### Example: `{WORKSPACE_ROOT}/GCP/my-project/cloud_run/architecture.md`
```markdown
# Cloud Run Architecture: my-project

## System Topology & Request Flow
The Cloud Run layer acts as the primary compute boundary for user-facing applications. 

- **`frontend`**: The main web interface. It scales from 0 to 100 based on HTTP traffic. It relies synchronously on `postgres-db` (Cloud SQL) for user profiles and asynchronously publishes to `events-topic` (Pub/Sub) for analytics telemetry.

## Architecture Graph
\`\`\`mermaid
graph TD
    Client((Client)) --> Frontend[Cloud Run: frontend]
    Frontend -->|Reads/Writes Profiles| DB[(Cloud SQL: postgres-db)]
    Frontend -->|Publishes Events| Async[Pub/Sub: events-topic]
    
    style Frontend fill:#326ce5,stroke:#fff,stroke-width:2px,color:#fff
\`\`\`
```

## Core Discovery Workflow

> 💡 **MCP Tip:** If your agent has the **GCP MCP server** connected (via `gcp-mcp-setup`), **always prefer MCP tools** over raw `gcloud` terminal commands for infrastructure discovery. MCP retrieves structured JSON directly, saving time and avoiding CLI parsing issues. **If MCP is not available or fails, use raw `gcloud` shell commands as a reliable fallback.**

### Incremental Discovery Pattern

**Step 1: Check Cache First**
```bash
# Agent checks documentation for architecture
# Files: GCP/{PROJECT_ID}/{CLOUD_PRODUCT}/state.json and architecture.md
```

**Step 2: Targeted Discovery from Alert**
- Alert mentions "frontend service" → discover only Cloud Run service named "frontend"
- Alert mentions "high CPU on GKE" → discover only that specific GKE cluster
- Alert mentions "database errors" → discover only Cloud SQL instances

**Step 3: Discover Dependencies (if needed)**
- Found Cloud Run service → check if it calls other services (via environment variables, service mesh)
- Found GKE service → check backend services it depends on
- Store dependency maps in the relevant `state.json` file.

**Step 4: Update Cache**
- Add newly discovered resources to `{PROJECT_ID}/{CLOUD_PRODUCT}/state.json`
- Update timestamps
- Generate/update the Mermaid graphs and context in `{PROJECT_ID}/{CLOUD_PRODUCT}/architecture.md`
- Run `python skills/gcp-architecture-discovery/scripts/render_architecture_png.py GCP/{PROJECT_ID}/{CLOUD_PRODUCT}/architecture.md` to generate a PNG graphic of the architecture.
- Append a standard Markdown image link referencing the generated PNG to the bottom of the `architecture.md` file (e.g., `![Topology](./architecture.png)`).

**Step 5: Document in Session**
- When working on an incident, update the respective `architecture.md` to reflect the latest known good state if discrepancies were found.
- Note any gaps or unknowns.

### Example: Incident-Driven Discovery

```bash
# Incident: "Frontend service returning 500 errors"

# 1. Discover the affected service (targeted)
gcloud run services describe frontend --region=us-central1 --format=json

# 2. Check recent deployments (was there a change?)
gcloud run revisions list --service=frontend --region=us-central1 --limit=5

# 3. Discover dependencies (from environment variables or docs)
# Frontend calls: backend-api, postgres-db

# 4. Discover backend service (incremental)
gcloud run services describe backend-api --region=us-central1 --format=json

# 5. Discover database (incremental)
gcloud sql instances describe postgres-db --format=json

# 6. Update cache with these 3 resources + dependencies
# 7. Continue investigation with monitoring/logs skills
```

### Targeted Discovery Commands (Preferred)

**Use these commands during investigations to discover ONLY what you need:**

#### Single Resource Discovery

```bash
# Discover ONE Cloud Run service
gcloud run services describe SERVICE_NAME --region=REGION --format=json

# Discover ONE GKE cluster
gcloud container clusters describe CLUSTER_NAME --region=REGION --format=json

# Discover ONE GCE instance
gcloud compute instances describe INSTANCE_NAME --zone=ZONE --format=json

# Discover ONE Cloud SQL instance
gcloud sql instances describe INSTANCE_NAME --format=json

# Discover ONE Cloud Function
gcloud functions describe FUNCTION_NAME --region=REGION --format=json

# Discover ONE storage bucket
gcloud storage buckets describe gs://BUCKET_NAME --format=json

# Discover ONE load balancer
gcloud compute forwarding-rules describe RULE_NAME --region=REGION --format=json
```

#### Filtered Discovery (by label, zone, or pattern)

```bash
# Cloud Run services with specific label
gcloud run services list --filter="metadata.labels.app=frontend" --format=json

# GKE clusters in specific region only
gcloud container clusters list --region=us-central1 --format=json

# GCE instances with specific tag
gcloud compute instances list --filter="tags.items:frontend" --format=json

# Recent revisions only (last 5)
gcloud run revisions list --service=SERVICE_NAME --limit=5 --format=json
```

### 1. Project-Level Discovery (Baseline Only)

**Use only when**: Setting up initial cache for a new project, or during major architecture review.

Start by identifying the GCP project and basic metadata:

```bash
# Get current project
gcloud config get-value project

# List all projects (if needed)
gcloud projects list

# Get project metadata
gcloud projects describe PROJECT_ID
```

### 2. Compute Resources Discovery (Bulk - Baseline Only)

**⚠️ Use only for initial baseline discovery, not during incidents.**

Identify all compute resources in the project:

#### Virtual Machines (GCE)
```bash
# List all VM instances
gcloud compute instances list --format="table(name,zone,machineType,status,networkInterfaces[0].networkIP:label=INTERNAL_IP,networkInterfaces[0].accessConfigs[0].natIP:label=EXTERNAL_IP)"

# Get detailed VM info
gcloud compute instances describe INSTANCE_NAME --zone=ZONE --format=json
```

#### Google Kubernetes Engine (GKE)
```bash
# List all GKE clusters
gcloud container clusters list --format="table(name,location,currentMasterVersion,currentNodeCount,status)"

# Get cluster details
gcloud container clusters describe CLUSTER_NAME --region=REGION

# List node pools
gcloud container node-pools list --cluster=CLUSTER_NAME --region=REGION

# Get kubectl context (after authenticating)
kubectl get nodes -o wide
kubectl get namespaces
kubectl get pods --all-namespaces -o wide
kubectl get services --all-namespaces
kubectl get deployments --all-namespaces
```

#### Cloud Run Services
```bash
# List all Cloud Run services
gcloud run services list --platform managed --format="table(SERVICE,REGION,URL,LAST_DEPLOYED)"

# Get service details
gcloud run services describe SERVICE_NAME --region=REGION --format=json

# List revisions
gcloud run revisions list --service=SERVICE_NAME --region=REGION
```

#### Cloud Functions
```bash
# List all Cloud Functions
gcloud functions list --format="table(name,status,trigger,region)"

# Get function details
gcloud functions describe FUNCTION_NAME --region=REGION
```

#### App Engine
```bash
# List App Engine services
gcloud app services list

# List versions
gcloud app versions list --service=SERVICE_NAME

# Get App Engine details
gcloud app describe
```

### 3. Networking Discovery (Bulk - Baseline Only)

**⚠️ Use only for initial baseline discovery, not during incidents.**

Map the networking architecture:

#### VPC Networks
```bash
# List VPC networks
gcloud compute networks list

# List subnets
gcloud compute networks subnets list --network=NETWORK_NAME --format="table(name,region,ipCidrRange,purpose)"

# List firewall rules
gcloud compute firewall-rules list --format="table(name,network,direction,priority,sourceRanges.list():label=SRC_RANGES,allowed[].map().firewall_rule().list():label=ALLOW)"
```

#### Load Balancers
```bash
# List forwarding rules (load balancers)
gcloud compute forwarding-rules list --format="table(name,region,IPAddress,target)"

# List backend services
gcloud compute backend-services list

# List URL maps
gcloud compute url-maps list
```

#### Cloud DNS
```bash
# List managed zones
gcloud dns managed-zones list

# List DNS records
gcloud dns record-sets list --zone=ZONE_NAME
```

### 4. Storage Resources Discovery (Bulk - Baseline Only)

**⚠️ Use only for initial baseline discovery, not during incidents.**

Identify storage systems:

#### Cloud Storage
```bash
# List buckets
gcloud storage buckets list --format="table(name,location,storageClass)"

# Get bucket details
gcloud storage buckets describe gs://BUCKET_NAME
```

#### Cloud SQL
```bash
# List Cloud SQL instances
gcloud sql instances list --format="table(name,database_version,region,gceZone,tier,primaryAddress.ipAddress:label=IP,state)"

# Get instance details
gcloud sql instances describe INSTANCE_NAME
```

#### Persistent Disks
```bash
# List disks
gcloud compute disks list --format="table(name,zone,sizeGb,type,status,users)"
```

### 5. Service Dependencies Discovery (Bulk - Baseline Only)

**⚠️ Use only for initial baseline discovery, not during incidents.**

Identify how services communicate:

#### Service Accounts
```bash
# List service accounts
gcloud iam service-accounts list --format="table(email,displayName,disabled)"

# List IAM policy bindings
gcloud projects get-iam-policy PROJECT_ID
```

#### API Services
```bash
# List enabled APIs
gcloud services list --enabled --format="table(NAME,TITLE)"

# List available APIs
gcloud services list --available
```

#### Service Mesh (if using Anthos/Istio)
```bash
# Get Istio configuration (if applicable)
kubectl get virtualservices --all-namespaces
kubectl get destinationrules --all-namespaces
kubectl get gateways --all-namespaces
```

### 6. Monitoring & Logging Discovery (Bulk - Baseline Only)

**⚠️ Use only for initial baseline discovery, not during incidents.**

Understand observability setup:

```bash
# List alert policies
gcloud alpha monitoring policies list --format="table(displayName,enabled,conditions)"

# List notification channels
gcloud alpha monitoring channels list

# List uptime checks
gcloud alpha monitoring uptime list

# Check logging setup
gcloud logging sinks list
```

## Cache Management

### Reading from Cache

**Agent / Human Process:**
```
1. Check if `GCP/{PROJECT_ID}/{CLOUD_PRODUCT}/state.json` exists
2. If exists and recent (< 24 hours old), use cached data
3. If exists but stale, consider refreshing specific resources
4. If doesn't exist, perform initial targeted discovery
```

**Querying the cache:**
```bash
# View cached cloud run services
cat GCP/my-project/cloud_run/state.json | jq '.instances'

# Check cache age
cat GCP/my-project/cloud_run/state.json | jq '.last_updated'

# List all tracked products
ls -la GCP/my-project/
```

### Updating Cache (Incremental)

**After discovering new resources:**
1. Read existing cache from `GCP/{PROJECT_ID}/{CLOUD_PRODUCT}/state.json`
2. Merge new discoveries with existing data
3. Update timestamps for modified resources
4. Sync dependencies/references array
5. Automatically reflect structural changes in `GCP/{PROJECT_ID}/{CLOUD_PRODUCT}/architecture.md` (e.g. update Mermaid graphs). Write back to both files.

**Example merge logic:**
```json
{
  "instances": [
    {"name": "frontend", "discovered_at": "2026-05-30T10:00:00Z"},  // existing
    {"name": "backend", "discovered_at": "2026-06-02T14:30:00Z"}    // newly discovered
  ]
}
```

### Refreshing Stale Cache

**When to refresh:**
- Deployments happened (check revision changes)
- Investigating infrastructure changes
- Cache older than 7 days for specific resource
- Resource suspected to be modified

**How to refresh:**
```bash
# Re-discover specific resource
gcloud run services describe frontend --region=us-central1 --format=json

# Agent updates only that resource in state.json and architecture.md, keeps others intact
```

### Cache Invalidation

**Clear cache when:**
- Major architecture changes confirmed
- Starting fresh baseline discovery
- Cache corrupted or inconsistent

**How to clear:**
```bash
# Remove specific project cache
rm -rf GCP/{PROJECT_ID}/
```

### Session Discovery Log

During each investigation, maintain or use the markdown architectural files:

**Whenever architecture is learned, create/update `architecture.md` in the product directory:**
```markdown
# Cloud Run Documentation
## Recent Findings (2026-06-02)
- Added 'backend' service dependency to 'frontend'
```

## Resources Discovered This Session

### Cloud Run Service: frontend
- **Status**: Cached (from 2026-05-30, fresh)
- **Current Revision**: frontend-00042-abc
- **Dependency**: backend-api, postgres-db

### Cloud Run Service: backend-api
- **Status**: Newly discovered (not in cache)
- **Current Revision**: backend-00015-xyz
- **Issue**: High error rate detected

### Cloud SQL: postgres-db
- **Status**: Cached (from 2026-05-25, needs refresh?)
- **Connection**: backend-api connects here

## Next Steps
- [ ] Check backend-api logs for database connection errors
- [ ] Verify postgres-db health metrics
```

## Creating Architecture Diagrams

After discovery, document the architecture:

### Using gcloud Resource Manager
```bash
# Export project structure
gcloud asset search-all-resources --scope=projects/PROJECT_ID --format=json > resources.json
```

### Visualization Recommendations

1. **Service Dependency Map**: Show how services call each other
2. **Network Topology**: VPCs, subnets, firewall rules, load balancers
3. **Data Flow**: How data moves through the system
4. **Authentication Flow**: Service accounts and IAM relationships

### Diagram Tools
- Use Mermaid diagrams for text-based architecture docs
- Google Cloud Architecture Diagramming Tool
- Draw.io with GCP icons

## Investigation Checklist (Incremental Discovery)

When investigating an incident, follow this incremental pattern:

1. ✅ **Check Alert/Ticket** - Identify affected service name/resource
2. ✅ **Check Cache First** - Look in `GCP/{PROJECT_ID}/` for existing info
3. ✅ **Targeted Discovery** - Discover ONLY the affected service (use `describe` not `list`)
4. ✅ **Recent Changes** - Check revisions/deployments for that service only
5. ✅ **Dependency Discovery** - Identify direct dependencies (from config/env vars)
6. ✅ **Incremental Expansion** - Discover dependencies one-by-one as needed
7. ✅ **Update Cache** - Merge new discoveries into the `state.json`
8. ✅ **Document Session** - Update the `architecture.md`
9. ✅ **Continue Investigation** - Move to monitoring/logs skills with discovered context

**❌ DON'T**: Run `list` commands for all resources in the project
**✅ DO**: Run `describe` commands for specific resources mentioned in alerts

## Common Patterns

### Microservices on GKE
- GKE cluster → Namespaces → Deployments → Pods
- Ingress → Services → Pods
- ConfigMaps and Secrets for configuration
- Cloud SQL or external databases

### Serverless Architecture
- Cloud Run services → Cloud SQL
- Cloud Functions → Pub/Sub → Cloud Storage
- API Gateway → Backend services

### Hybrid Architecture
- GKE for stateful services
- Cloud Run for stateless APIs
- Cloud Functions for event processing
- Mix of GCE VMs for legacy applications

## Safe Mode Support

This skill respects `SAFE_MODE="enabled"` and will only use read-only commands. All discovery operations are non-mutating and safe to run during incidents.

## Related Skills

- **gcp-mcp-setup**: Setup Google Cloud MCP server. Highly recommended for agents as it provides native, structural API discovery instead of screen-scraping CLI output!
- **gcp-setup**: Verify authentication before discovery
- **gcp-playbooks**: Use discovered architecture for mitigation
- **cloud-monitoring**: Query metrics for discovered resources
- **investigation-entrypoint**: Start here when responding to incidents

## Tips & Best Practices

1. **Prefer MCP over CLI (but use CLI as fallback)**: If connected, use GCP MCP tools for structured API exploration instead of invoking `gcloud` locally, as it perfectly fits the agent's JSON capabilities. If MCP is missing or lacking specific access, fall back to standard `gcloud` commands.
2. **Start Narrow, Expand as Needed**: Begin with the affected service, then discover dependencies incrementally
3. **Check Cache First**: Always check `GCP/{PROJECT_ID}/` before running discovery commands
4. **Use `describe` not `list`**: Target specific resources by name, not bulk operations
5. **Leverage Labels & Filters**: Use resource labels to find related resources efficiently
5. **Update Cache Incrementally**: Merge new discoveries, don't overwrite entire cache
6. **Document in Session Notes**: Keep notes and update `architecture.md` on what you discovered and why during investigations
7. **Refresh Selectively**: Only re-discover resources when you suspect changes
8. **Trust the Cache**: If discovery was recent (< 24h), rely on cached data unless investigating infrastructure changes
9. **Dependency Mapping**: Track service dependencies in cache for faster future investigations
10. **Verify Access Once**: Check IAM permissions at session start, cache the verification

## Troubleshooting

### Permission Denied Errors
```bash
# Check current account
gcloud auth list

# Verify IAM permissions
gcloud projects get-iam-policy PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:user:YOUR_EMAIL"
```

### Incomplete Results
- Check if resources are in different regions/zones
- Verify filters aren't too restrictive
- Ensure APIs are enabled: `gcloud services list --enabled`

### Stale Cache Data
- Check cache timestamp: is it older than expected?
- Refresh specific resource: re-run `describe` command
- If major changes occurred, consider clearing cache and re-discovering

### Resource Not Found
- Verify resource name spelling (case-sensitive)
- Check if resource is in expected region/zone
- Confirm resource still exists (may have been deleted)
- Update cache to remove deleted resources

## Examples

### Example 1: Incident Investigation (Incremental Discovery)
```bash
# Alert: "Cloud Run service 'frontend' returning 500 errors"

# Step 1: Check cache first
# cat GCP/myproject/cloud_run/state.json
# cat GCP/myproject/cloud_run/architecture.md

# Step 2: Discover affected service
gcloud run services describe frontend --region=us-central1 --format=json

# Step 3: Check recent changes
gcloud run revisions list --service=frontend --limit=5

# Step 4: Discover dependencies (from service env vars or documentation)
# Found: BACKEND_URL=https://backend-api-xxx.run.app, DB_HOST=postgres-db

# Step 5: Discover backend incrementally
gcloud run services describe backend-api --region=us-central1 --format=json

# Step 6: Discover database incrementally
gcloud sql instances describe postgres-db --format=json

# Agent updates cache with these 3 resources + dependencies
# Continue with cloud-monitoring skill for metrics
```

### Example 2: Using Labels for Targeted Discovery
```bash
# Find all frontend-related resources (incremental, filtered)
gcloud asset search-all-resources \
  --scope=projects/PROJECT_ID \
  --query="labels.component=frontend" \
  --format="table(name,assetType,location)"
```

### Example 3: Dependency Chain Discovery
```bash
# Starting from load balancer, trace to backend
# 1. Find load balancer
gcloud compute forwarding-rules describe my-lb --region=us-central1

# 2. Find backend service
gcloud compute backend-services describe my-backend --global

# 3. Find instance group or NEG
gcloud compute instance-groups describe my-ig --zone=us-central1-a
```

## Version History

### 0.1.0 - Initial Release
- Incremental discovery approach with state management
- Repository and session memory integration for caching
- Targeted discovery commands (describe vs list)
- Cache management with merge and refresh strategies
- Investigation checklist optimized for incident response
- Incident-driven discovery pattern
