# Cloud Resource Manager & Discovery Playbooks
API Name: `cloudresourcemanager.googleapis.com` (and `cloudasset.googleapis.com`)

This playbook covers how to interact with the Cloud Resource Manager and Cloud Asset APIs to discover infrastructure, project metadata, and IAM policies.

Using the **Cloud Asset API** is the fastest way to perform cross-project discovery in a single API call.

## Infrastructure Discovery

When investigating an incident, start by identifying the scope and types of resources involved. Use `cloudresourcemanager` to get project information and `cloudasset` to list resources.

Be particularly interested in the following asset types during an investigation:

- **Infrastructure/Compute:**
  - Cloud Run: `run.googleapis.com/Service` (`run.md`)
  - GKE: `container.googleapis.com/Cluster` (`container.md`)
  - GCE: `compute.googleapis.com/Instance`
- **Operations:**
  - Logging: `logging.googleapis.com/LogBucket`
  - Monitoring: `monitoring.googleapis.com/AlertPolicy`
- **Security:**
  - IAM: `iam.googleapis.com/Role` or `iam.googleapis.com/ServiceAccount`
  - Secret Manager: `secretmanager.googleapis.com/Secret`
- **Storage & Databases:**
  - Cloud Storage: `storage.googleapis.com/Bucket`
  - Cloud SQL: `sqladmin.googleapis.com/Instance`
  - AlloyDB: `alloydb.googleapis.com/Cluster` or `alloydb.googleapis.com/Instance`
  - Firestore: `firestore.googleapis.com/Database`
  - BigQuery: `bigquery.googleapis.com/Dataset`
  - Spanner: `spanner.googleapis.com/Instance`
- **Events & Messaging:**
  - Pub/Sub: `pubsub.googleapis.com/Topic` or `pubsub.googleapis.com/Subscription`
  - Cloud Run Functions: `cloudfunctions.googleapis.com/Function`
- **CI/CD:**
  - Artifact Registry: `artifactregistry.googleapis.com/Repository`
  - Cloud Build: `cloudbuild.googleapis.com/Build` (`cloudbuild.md`)
  - Cloud Deploy: `clouddeploy.googleapis.com/DeliveryPipeline` or `clouddeploy.googleapis.com/Release`

## Mitigations & Discovery Actions

### Project Discovery

When starting an investigation, verify the project exists, its state, and its parent organization or folder.

**Manual Actuation (gcloud):**
```bash
gcloud projects describe PROJECT_ID
```

### Billing Status Check

Verify that billing is enabled for the project. If `billingEnabled` is `false`, resources (GCE, GKE, etc.) will be stopped or unreachable.

**Actuation (gcloud):**
```bash
gcloud billing projects describe PROJECT_ID
```

### Cross-Project Resource Discovery (Single API Call)

If the issue is considered to be across multiple projects (e.g., "project1-frontend", "project2-backend", and "project3-database"), use the **Cloud Asset Inventory** to search for resources across the entire scope in one call.

**Actuation (gcloud Asset Search):**
```bash
# Search across multiple projects using a common parent (e.g., your organization)
gcloud asset search-all-resources \
  --scope=organizations/YOUR_ORG_ID \
  --asset-types="run.googleapis.com/Service,sqladmin.googleapis.com/Instance,storage.googleapis.com/Bucket" \
  --query="project:(project1-frontend OR project2-backend OR project3-database)" \
  --format="table(name, assetType, project)"
```

### IAM Policy Investigation

If there are permission errors, check the project-level IAM policy.

**Actuation (gcloud):**
```bash
gcloud projects get-iam-policy PROJECT_ID
```

## MCP investigation

For AI agents equipped with the Gemini MCP integration, the `cloudresourcemanager` tools provide the fastest way to correlate resources across multiple projects autonomously.

**Project Discovery Tool:** `mcp_google-resourcemanager_search_projects`
- **List all accessible projects:** Call the tool with an empty payload to get metadata (IDs, parent organizations, labels) for N projects.
- **Filter by query:** Call with the `query` parameter (e.g., `query="name:sre-*"` or `query="parent.id:867259228481"`) to narrow down the scope of your investigation.
