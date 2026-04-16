# Command Risk Assessment Format

When suggesting commands for the user to run, preface the command with a risk assessment block in the following format:

```bash
# 🎬 <Action description in a few words>
# ⚠️ Risk: <Emoji> <LEVEL>: <Brief explanation of risks and potential impact.>
# [Optional: Note on why this risk level was chosen]
# [Optional: Mitigation steps or things to watch out for]
<command to execute>
```

**Risk Levels & Emojis:**

*   **🔴 HIGH:** Significant potential to cause service disruption, data loss, or security issues. Requires careful consideration and understanding.
    *   *Examples:* Deleting resources, modifying production IAM policies, draining nodes.
*   **🟡 MEDIUM:** Potential to cause temporary unavailability or performance degradation. User should be aware of the impact.
    *   *Examples:* Restarting instances, rolling updates, resizing clusters.
*   **🟢 LOW:** Minimal risk of negative impact. Operations are generally safe and reversible.
    *   *Examples:* Scaling down non-critical replicas, applying minor configuration changes.
*   **⚪ NONE:** Read-only operations or actions with no impact on the service state.
    *   *Examples:* Listing resources, viewing logs, getting configurations.

**Example: HIGH Risk**

```bash
# 🎬 Delete GKE cluster
# ⚠️ Risk: 🔴 HIGH: This is irreversible and will delete all workloads and data in the cluster.
# Ensure this is the intended cluster and all data is backed up.
gcloud container clusters delete <cluster-name> --zone <zone>
```

**Example: MEDIUM Risk**

```bash
# 🎬 Restart GCE instance
# ⚠️ Risk: 🟡 MEDIUM: The instance will be temporarily unavailable during the restart.
gcloud compute instances reset <instance-name> --zone <zone>
```

**Example: NONE Risk**

```bash
# 🎬 List pods in namespace
# ⚠️ Risk: ⚪ NONE: This is a read-only operation.
kubectl get pods -n <namespace>
```
