---
name: gcp-architecture-discovery
description: 🐉 [SRE] Discover and map GCP infrastructure architecture including compute, networking, storage, and service dependencies. Use when the user asks to "investigate", "check", or "troubleshoot" an issue (incremental mode) or explicitly requests to map the system. 
metadata:
  author: sstawski
  version: 0.1.0
  status: draft
---

# GCP Architecture Discovery

## Overview

This skill provides an **incremental discovery** approach for GCP infrastructure. Instead of scanning everything at once, it discovers only what's needed for the current investigation and caches results for future use.

## When to Use

- **Active Incidents (Triggers: "investigate", "check", "troubleshoot", "why is X down")**: When investigating a failing service or starting an incident response. **Must use MODE 2 (Incremental)**.
- **Onboarding/Setup (Triggers: "baseline", "discover all", "map the project")**: When initializing a new GCP project for the first time. **Must use MODE 1 (Initial/Full)**.
- Following up on alerts - discover only the implicated resources.
- Identifying dependencies between services during incidents.
- Creating architecture diagrams for postmortems.
- Auditing specific resource configurations.

### Discovery Strategy: Dual Modes (Baseline vs Incident)

### Philosophy & Agent Mindset

**The Architecture Graph is Your Mental Model.**
The `discover.json` and generated PNG do not have to be a perfect, eternal reflection of the actual cloud infrastructure. They represent *how you see the system right now*. **Do not hesitate** to update, rewrite, or expand the graph whenever you discover something new. If you realize a Load Balancer connects to a different backend than previously drawn, overwrite it immediately. The graph is your working scratchpad.

We employ **two strict discovery modes**. The mode is determined by which SKILL invoked this architecture discovery process:

**MODE 1: Initial/Full Discovery (Baseline)**
- **Invocation Context**: Use this mode when performing the initial environment setup, establishing a baseline, or when explicitly requested to do a full scan by the user.
- **Discover EVERYTHING.** Map the ENTIRE infrastructure.
- List all active resources (Compute, Storage, Network, DBs, IAM, Messaging) running in the project.
- Aggressively trace ALL dependencies.
> 🚨 **CRITICAL RULE FOR MODE 1:** NEVER stop after discovering a single resource. You MUST forcefully map all GKE, Cloud Run, VMs, Virtual Networks, Firewalls, Load Balancers, Cloud SQL, etc. Do not truncate the baseline map!

**MODE 2: Incremental Discovery (Incidents)**
- **Invocation Context**: Use this mode ONLY when investigating an active outage/alert, or when the user prompts you to *"investigate"*, *"check"*, *"troubleshoot"*, or *"find out what's wrong"* with a specific system.
- During incidents, exhaustive scanning wastes critical mitigation time.
- Start ONLY from the **affected service** indicated in the alert.
- **Discover dependencies incrementally**: Map its direct upstream callers (Load Balancers/Gateways) and downstream targets (DBs/Topics) needed exclusively for the investigation context.
- **Update Cache**: Merge this targeted slice into the existing graph without destroying the rest of the topology.

### State Management

> 🚨 **CRITICAL RULE: MANDATORY OUTPUT GENERATION**
> Setting up or updating the discovery folder structure is **NOT OPTIONAL**. Every time this skill is triggered, you **MUST ALWAYS** create or update the corresponding target folder, `.json`, `.md` and generate the `.png` visualization accurately. Never leave the data exclusively in the chat context. 

This skill uses a tool-agnostic, local file-based topology documentation approach.

The folder structure **MUST** be strictly organized as follows:
`{AGENT_WORKSPACE_ROOT}/discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_SUBSCRIPTION_NAME}/`

Inside each project/subscription directory, maintain these explicit files:

1. **`discover.json` (Structured Data Cache)**:
   - Contains a list of instances.
   - Contains references/dependencies to other resources.
   - Holds the raw Mermaid code inside a `"mermaid"` key for rendering.
   - Easy for the agent to parse programmatically.

2. **`wiki.<category>.md` (Topological Documentation by Resource Type)**:
   - Contains markdown documentation explaining how these pieces of architecture work together, separated into distinct files based on resource category (e.g., `wiki.gce.md` for VMs, `wiki.vnet.md` for networks, `wiki.cloudrun.md` for Cloud Run, `wiki.sql.md` for databases).
   - One file, `wiki.overview.md`, MUST contain the main topology image link (`![Topology](./discover.png)`) and the high-level project description.
   - **MANDATORY STRUCTURE**: Each resource/app running on GCP MUST be documented under an `##` (H2) header inside its respective category file.
   - Important sub-points (such as properties, dependencies, configurations) MUST use `###` (H3) or `####` (H4) headers under the respective resource.
   - All resources/apps must explicitly list their most important properties (e.g., regions, versions, tier/scaling limits) and their dependencies.
   - **Do NOT embed raw Mermaid markdown code in any wiki file.**
   - Easy for humans and reasoning models to read contexturally.

### Cache Structure Examples

#### Example: `{WORKSPACE_ROOT}/discover/gcp-project/my-project/discover.json`
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
  },
  "mermaid": "graph TD\n    Client((Client)) -->|Ingress/HTTPS| LB[Cloud Load Balancer]\n    \n    subgraph \"VPC: my-main-vpc\"\n        subgraph \"Subnet: us-central1 / Firewall: allow-web-traffic\"\n            LB --> Frontend[Cloud Run: frontend]\n            Frontend -->|Reads/Writes Profiles| DB[(Cloud SQL: postgres-db)]\n        end\n    end\n\n    Frontend -->|Publishes Events| Async[Pub/Sub: events-topic]\n    \n    style Frontend fill:#326ce5,stroke:#fff,stroke-width:2px,color:#fff\n    style LB fill:#8b42f5,stroke:#fff,stroke-width:2px,color:#fff"
}
```

#### Example: `{WORKSPACE_ROOT}/discover/gcp-project/my-project/wiki.overview.md`
```markdown
# Infrastructure Overview: my-project

## Architecture Graph
![Topology](./discover.png)
```

#### Example: `{WORKSPACE_ROOT}/discover/gcp-project/my-project/wiki.cloudrun.md`
```markdown
# Cloud Run Resources

## Cloud Run: frontend
The Cloud Run layer acts as the primary compute boundary for user-facing applications. 

### Properties
- **Region**: us-central1
- **Scaling**: 0 to 100 max instances
- **Ingress**: Internal and Cloud Load Balancing

### Dependencies
- **Synchronous**: Relies on `postgres-db` (Cloud SQL) for user profiles.
- **Asynchronous**: Publishes to `events-topic` (Pub/Sub) for analytics telemetry.
```

#### Example: `{WORKSPACE_ROOT}/discover/gcp-project/my-project/wiki.sql.md`
```markdown
# Cloud SQL Resources

## Cloud SQL: postgres-db
Relational database storing user metadata.

### Properties
- **Version**: PostgreSQL 14
- **Tier**: db-custom-2-7680
- **High Availability**: Enabled (Regional)

### Dependencies
- **Upstream callers**: `frontend`
```

## Core Discovery Workflow

> 💡 **MCP Tip:** If your agent has the **GCP MCP server** connected (via `gcp-mcp-setup`), **always prefer MCP tools** over raw `gcloud` terminal commands for infrastructure discovery. MCP retrieves structured JSON directly, saving time and avoiding CLI parsing issues. **If MCP is not available or fails, use raw `gcloud` shell commands as a reliable fallback.**

### Comprehensive Discovery Pattern

**Step 1: Check Cache First**
```bash
# Agent checks documentation for architecture
# Files: ./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/discover.json and ./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/wiki.md
```

**Step 2: Choose Mode based on Invocation Context**
- If triggered during an active incident/outage investigation: Proceed with **Step 2B: Targeted Incident Sweep**.
- If triggered during initial setup or explicitly asked for a baseline: Proceed with **Step 2A: Aggressive Project-Wide Sweep**.

**Step 2A: Aggressive Project-Wide Sweep (MODE 1 Initial/Full)**
- Query GCP to list all core resources. Do not rely on assumptions.
- Run `gcloud compute instances list`
- Run `gcloud run services list`
- Run `gcloud container clusters list`
- Run `gcloud sql instances list`
- Search everything: `gcloud asset search-all-resources --scope=projects/PROJECT_ID`
- Identify EVERY service, DB, and storage bucket running in the project.

**Step 2B: Targeted Incident Sweep (MODE 2 Incremental)**
- Start from the alert text (e.g., "high CPU on frontend").
- Discover ONLY the affected node (e.g., `gcloud run services describe frontend`).
- Identify direct upstream callers and downstream dependencies. DO NOT scan the whole project.

**Step 3: Discover Dependencies & Network Layers**
- For the discovered compute services → check if they call other services (via environment variables, service mesh). Determine Serverless VPC Access connections if any.
- For the discovered GKE services → check backend services they depend on. Inspect VPC, subnets, and Network Policies.
- **Discover Network & Security Layers**: Identify and explicitly map ALL Virtual Networks (VPCs, Subnets), Security Perimeters (e.g., VPC Service Controls, IAP boundaries), Firewalls, Cloud NAT, and Load Balancers routing the traffic. Map all ingress/egress boundaries for your scope.
- Store this dependency map, security boundaries, and network topologies in the relevant `discover.json` file.


**Step 4: 🛑 MANDATORY TOOL EXECUTION - Update Cache**
You **MUST always perform this step**. Never skip saving your discoveries to disk. **Do not hesitate** to update the cache—this is your active mental model. Overwrite outdated assumptions immediately.
**CRITICAL:** You must physically execute the `replace_string_in_file` or `create_file` tools to update these files *BEFORE* responding to the user.
- Add newly discovered resources to `./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/discover.json`. Create the file/directory if it does not exist.
- Update timestamps inside `discover.json`.
- Update the context in the respective `./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/wiki.<category>.md` files based on resource type (e.g., `wiki.vnet.md`, `wiki.gce.md`). Create the files if they do not exist. Ensure there are NO raw mermaid blocks inside any wiki file.
- Save the raw Mermaid code inside the `"mermaid"` key of `./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/discover.json`.
- **CRITICAL GRAPHING RULE**: The Mermaid graph **MUST visually encompass all topological layers**. You must map EVERY resource and application into proper `subgraph` structures that represent their actual Network boundaries (Virtual Networks, VPCs, Subnets), Security Perimeters (VPC Service Controls, IAM domains), and Firewall rules (ingress/egress policies). No compute resource should "hang flat" without its network/security context.
- Run `python skills/gcp-architecture-discovery/scripts/render_architecture_png.py ./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/discover.json` to generate a PNG graphic of the architecture.
- Ensure the main image link referencing the generated PNG is placed in `./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/wiki.overview.md` (e.g., `![Topology](./discover.png)`).

**Step 5: Document in Session**
- When working on an incident, update the respective `wiki.<category>.md` files to reflect the latest known good state if discrepancies were found.
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

# Discover ONE VPC Network / Firewalls
gcloud compute networks describe NETWORK_NAME --format=json
gcloud compute firewall-rules list --filter="network:NETWORK_NAME" --format=json
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

## Investigation Checklist

1. ✅ **Check Cache First** - Look in `./discover/` for existing info
2. ✅ **Choose Discovery Mode** - Use Comprehensive mode if building the baseline. Use Targeted mode if investigating an active incident.
3. ✅ **Discover Networks** - Identify VPCs, Firewalls, Load Balancers, and Security Perimeters around your target scope.
4. ✅ **Dependency Discovery** - Investigate env vars, IAM boundaries, and connections to map relationships.
5. ✅ **Update Cache** - Write ALL discovered resources into the `discover.json` graph and references.
6. ✅ **Document Session** - Update the respective `wiki.<category>.md` (e.g. `wiki.gce.md`, `wiki.vpc.md`) files and visually map EVERY object in the Mermaid graph inside its network perimeter.
7. ✅ **Continue Investigation** - Move to monitoring/logs skills with complete context.

**❌ DON'T**: Run an exhaustive sweep if you are actively investigating an acute incident.
**✅ DO**: Map the *entire* footprint of a service when performing targeted discovery (e.g., if you look at a Storage account, you must map the App that calls it, the VPC it lives in, and the Firewall protecting it).

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
- **gcp-playbooks**: Use discovered architecture for mitigation
- **cloud-monitoring**: Query metrics for discovered resources

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
