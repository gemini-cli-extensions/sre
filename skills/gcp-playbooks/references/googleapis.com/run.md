# Cloud Run Playbooks
API Name: `run.googleapis.com`

This playbook maps generic SRE mitigation strategies to specific Google Cloud Run actuations.

## Mitigations

### Rollback (binary_rollback / cdpush_rollback)

In the context of Cloud Run, a "rollback" means shifting 100% of the traffic from the current (failing) revision back to a previously known-good revision.

**What it means:** Cloud Run automatically creates a new immutable "Revision" every time you deploy a new image or change the service configuration. Rolling back involves updating the service's traffic split to point to an older revision ID.

**Actuation (gcloud):**
```bash
# 1. Identify the previous good revision
gcloud run revisions list --service=SERVICE_NAME --region=REGION --project=PROJECT_ID

# 2. Update traffic to the previous good revision (e.g., service-name-00001-abc)
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=PREVIOUS_REVISION_ID=100 \
  --region=REGION --project=PROJECT_ID
```

### Fix Forward (binary_fix_forward)

A "fix forward" means deploying a new container image containing a patch or reverting the offending code in source control and pushing a new release, rather than reverting to an old revision.

**What it means:** You build a new image and deploy it. Cloud Run will automatically create a new revision and route 100% of traffic to it (by default).

**Actuation (gcloud):**
```bash
gcloud run deploy SERVICE_NAME \
  --image=NEW_IMAGE_URL \
  --region=REGION --project=PROJECT_ID
```

### Upsize (upsize)

"Upsizing" in Cloud Run generally means increasing the maximum number of instances to handle increased load or preventing rate limiting/throttling. It can also mean increasing CPU/Memory allocations if the containers are OOMing or CPU-starved.

**What it means:** You modify the service configuration to raise the `--max-instances` limit, or increase the `--cpu` and `--memory` limits. This creates a new revision.

**Actuation (gcloud):**
```bash
# Increase max instances
gcloud run services update SERVICE_NAME \
  --max-instances=NEW_MAX \
  --region=REGION --project=PROJECT_ID

# Increase memory/CPU
gcloud run services update SERVICE_NAME \
  --memory=2Gi --cpu=2 \
  --region=REGION --project=PROJECT_ID
```

### Traffic Drain (traffic_drain)

"Traffic drain" in Cloud Run is typically handled via Load Balancing (Cloud Load Balancing) if sitting in front of Cloud Run, or by shifting traffic away from a specific region in a multi-region deployment.

**What it means:** If a specific region is failing, you update your Global HTTP(S) Load Balancer to stop routing traffic to the backend service associated with the failing Cloud Run region.

*Note: Native Cloud Run traffic splitting applies to revisions within the same region, not across regions. To drain a region, you must manage it at the load balancer level.*

### Degrade

Cloud Run does not have a native "degrade" button. Degradation usually involves pushing a configuration change (e.g., environment variables) to the application itself to disable non-critical features, which requires an application-level implementation.

### Restart (restart_task / restart_job)

Cloud Run is serverless. You cannot "restart" a specific container instance manually.
If an instance is misbehaving, it will eventually be killed by Cloud Run if it fails health checks, or you can force a new deployment/revision to cycle all instances.

**Actuation:** Deploying a new revision with no changes forces new instances.
```bash
gcloud run services update SERVICE_NAME \
  --update-env-vars="FORCE_RESTART=$(date +%s)" \
  --region=REGION --project=PROJECT_ID
```