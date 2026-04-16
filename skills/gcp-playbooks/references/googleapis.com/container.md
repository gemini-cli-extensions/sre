# Google Kubernetes Engine (GKE) Playbooks
API Name: `container.googleapis.com`

This playbook maps generic SRE mitigation strategies to specific GKE (Kubernetes) actuations.

## Mitigations

### Rollback (binary_rollback)

In GKE, a rollback typically applies to a Kubernetes `Deployment` or `StatefulSet`. It means reverting the object's template (usually the container image version) back to a previous state.

**What it means:** Kubernetes maintains a history of ReplicaSets for each Deployment. Rolling back instructs the Deployment controller to scale up an older ReplicaSet and scale down the current one.

**Actuation (kubectl):**
```bash
# 1. View rollout history to find the previous revision
kubectl rollout history deployment/DEPLOYMENT_NAME -n NAMESPACE

# 2. Undo the rollout (reverts to the immediately previous revision)
kubectl rollout undo deployment/DEPLOYMENT_NAME -n NAMESPACE

# Or, rollback to a specific revision
kubectl rollout undo deployment/DEPLOYMENT_NAME --to-revision=REVISION_NUMBER -n NAMESPACE
```

### Fix Forward (binary_fix_forward)

A "fix forward" means deploying a new configuration or container image rather than reverting.

**What it means:** You update the `Deployment` with a new container image tag. This triggers a RollingUpdate (by default), gradually replacing old Pods with new ones.

**Actuation (kubectl):**
```bash
kubectl set image deployment/DEPLOYMENT_NAME CONTAINER_NAME=NEW_IMAGE_URL -n NAMESPACE
```

### Upsize (upsize)

"Upsizing" in GKE can mean two things: increasing the number of Pods (Horizontal Scaling) or increasing the resources available to the cluster (Node Pool scaling).

**What it means (Pods):** Increasing the `replicas` count of a Deployment.
**What it means (Nodes):** Increasing the size of the underlying GKE Node Pool so more Pods can be scheduled.

**Actuation (Pods - kubectl):**
```bash
kubectl scale deployment/DEPLOYMENT_NAME --replicas=NEW_COUNT -n NAMESPACE
```

**Actuation (Nodes - gcloud):**
```bash
gcloud container clusters resize CLUSTER_NAME \
  --node-pool=NODE_POOL_NAME \
  --num-nodes=NEW_COUNT \
  --region=REGION --project=PROJECT_ID
```

### Traffic Drain / Quarantine (traffic_drain / quarantine)

Draining traffic in Kubernetes usually means taking a Node out of service, or removing a Pod from a Service's endpoint list without killing it immediately (Quarantine).

**What it means (Node Drain):** Evicting all Pods from a specific Node and marking it unschedulable. Useful if a specific VM is failing.
**What it means (Pod Quarantine):** Changing the labels on a failing Pod so that it no longer matches the `Service` selector. It stops receiving traffic but stays alive for debugging.

**Actuation (Node Drain - kubectl):**
```bash
# Mark node unschedulable and evict pods
kubectl drain NODE_NAME --ignore-daemonsets --delete-emptydir-data
```

**Actuation (Pod Quarantine - kubectl):**
```bash
# Overwrite the label that the Service uses to route traffic
# Assuming the Service routes based on 'app=my-service'
kubectl label pod POD_NAME app=my-service-quarantined --overwrite -n NAMESPACE
```

### Restart (restart_task / restart_job)

In Kubernetes, you don't restart a container; you delete the Pod, and the controller (Deployment/ReplicaSet) creates a new one.

**What it means (Single Task):** Deleting a specific Pod.
**What it means (Whole Job):** Triggering a rollout restart for the entire Deployment, which gracefully replaces all Pods one by one.

**Actuation (Single Pod - kubectl):**
```bash
kubectl delete pod POD_NAME -n NAMESPACE
```

**Actuation (All Pods - kubectl):**
```bash
kubectl rollout restart deployment/DEPLOYMENT_NAME -n NAMESPACE
```