---
name: gcp-architecture-discovery
description: 🐉 [SRE] Discover and map GCP infrastructure architecture including compute, networking, storage, and service dependencies.
metadata:
  author: sstawski
  version: 0.1.1
---

# GCP Architecture Discovery

## Overview

This skill provides a **discovery** approach for GCP infrastructure. It discovers what's needed for the current investigation and caches results for future use.

## When to Use

- When investigating a failing service or starting an incident response.
- When an incident has been resolved and the system topology has changed (e.g., firewall blocked an IP, traffic diverted).
- When initializing a new GCP project for the first time.
- Identifying dependencies between services during incidents.
- Creating architecture diagrams for human and agent understanding.
- Auditing specific resource configurations.

### Philosophy & Agent Mindset

**The Architecture Graph is Your Mental Model.**
The `discover.json` and generated PNG represent *how you see the system right now*. **Do not hesitate** to update, rewrite, or expand the graph whenever you discover something new. For example: If you realize a Load Balancer connects to a different backend than previously drawn, overwrite it immediately.

**Discovery Strategy (Adaptive Blast Radius)**
Exhaustive scans of an entire massive project waste time, but lazily scanning just one node *causes you to miss critical infrastructure changes* (e.g. altered firewalls, deleted databases, changed IAM policies).
- **Find the Anchor**: Start at the service or node experiencing the incident.
- **Map the Full Blast Radius**: You MUST aggressively discover and map ALL resources functionally or topologically connected to the anchor. This includes checking:
  - Upstream Load Balancers or API Gateways.
  - Surrounding Network boundaries (VPCs, Subnets, Firewalls, NATs). Did any rules change?
  - Downstream targets (Databases, Pub/Sub topics, Cloud Storage). Do they still exist?
> 🚨 **CRITICAL RULE:** NEVER stop after discovering just the single affected resource. You MUST forcefully map its entire surrounding ecosystem. Relying on old cache assumptions causes you to miss deleted, unmapped, or altered infrastructure.
- **Update Cache**: Merge the discovered ecosystem slice into the existing graph.

### State Management

> 🚨 **CRITICAL RULE: MANDATORY OUTPUT GENERATION**
> Setting up or updating the discovery folder structure is **NOT OPTIONAL**. Every time this skill is triggered, you **MUST ALWAYS** create or update the corresponding target folder, `.json`, `.md` and generate the `.png` visualization accurately. Never leave the data exclusively in the chat context.

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
   - Easy for humans and reasoning models to read contextually.

## Core Discovery Workflow

**Step 1: Check Cache First**
```bash
# Agent checks documentation for architecture
# Files: ./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/discover.json and ./discover/{gcp-project|azure-subscription}/{PROJECT_ID_OR_NAME}/wiki.*.md
```

**Step 2: Discovery Sweep (Blast Radius)**
- Query GCP to `list` or `describe` core resources connected to the incident. Do not rely on old cache assumptions—if a resource is throwing errors, verify its existence, its properties, and its relations.
- Identify everything in the event's blast radius: services, DBs, storage buckets, VPCs, Firewalls, and their direct upstream callers/downstream dependencies. Look out for missing, newly created, or modified resources in this radius.

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

**Step 5: Document in Session**
- When working on an incident, update the respective `wiki.<category>.md` files to reflect the latest known good state if discrepancies were found.
- Note any gaps or unknowns.

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
2. **Start Narrow, Expand as Needed**: Begin with the target service, then discover dependencies iteratively.
3. **Use `describe`** over `list` during incidents**: Target specific resources by name to save time, rather than performing bulk operations.
4. **Update Cache Incrementally**: When discovering new context, merge new discoveries into `discover.json`. Don't overwrite the entire cache unless performing a baseline regeneration.
5. **Trust the Mental Model**: If your `discover.json` cache is recent, rely on it to make architectural decisions quickly during an outage. Only refresh specific resource nodes when you suspect they've undergone recent changes (e.g. recent deployments).