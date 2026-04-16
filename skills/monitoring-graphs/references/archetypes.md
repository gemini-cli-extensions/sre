# 🏛️ Monitoring Archetypes Reference

Use these "Apple-to-Apple" strategies to find the "Broken Equilibrium" signal.

## 🏗️ Compute (GKE / Cloud Run)
- **Primary Signal:** HTTP 5xx error count or rate.
- **Secondary Signal:** Request latency (P95/P99 spikes), CPU/Memory throttling events.
- **Monitoring MCP Query:** Search for `kubernetes.io/container/restart_count` or `run.googleapis.com/request_count`.
- **Window:** Usually 5m alignment is enough to see the spike.

## 🌐 Network (VPC / Load Balancing)
- **Primary Signal:** Throughput drop (I/O) or packet loss.
- **Secondary Signal:** Backend connection errors, firewall drops.
- **Monitoring MCP Query:** `loadbalancing.googleapis.com/l3/external/ingress_bytes_count`.
- **Window:** Look for "cliffs" where traffic drops to zero and then recovers.

## 🗄️ Database (Cloud SQL / Spanner)
- **Primary Signal:** Transaction latency or lock wait times.
- **Secondary Signal:** Connection pool saturation, disk I/O wait.
- **Monitoring MCP Query:** Search for `cloudsql.googleapis.com/database/postgresql/transaction_count`.
- **Window:** 1m alignment to capture short-lived lock contention.

## 🌈 Progressive Rollout (Blue/Green)
- **The Dream:** Visualize version A (Green) fading out while version B (Blue) fades in.
- **Apple-to-Apple:** Use the `--stacked` flag for a **Stacked Area Chart**.
- **Diagnosis:** The total area should remain constant (100% capacity) while the colors shift. Non-linear curves show the "Canary -> 25% -> 50% -> 100%" progression.
- **Monitoring MCP Query:** `kubernetes.io/pod/status/phase` (Status: Running) grouped by `pod_template_hash`.

## 🏗️ Capacity vs Demand (Scaling Limits)
- **The Signal:** Current Instance Count vs. Min/Max configuration.
- **Apple-to-Apple:** Plot `instance_count` with horizontal lines (`--hmin`, `--hmax`).
- **Diagnosis:** If count is pinned at `max_instances` while latency spikes, you are under-provisioned.

## 🛠️ Data Extraction Strategy
| Phase | Granularity | Performance |
| :--- | :--- | :--- |
| **Discovery** | 1h or 1d | 🚀 Fast |
| **Investigation** | 15m or 1h | ⚖️ Balanced |
| **Post-Mortem** | 1m or 5m | 🐢 Slow |

- **Cleanup:** Always use `pandas` to fill or drop NaN values before plotting to avoid gaps in the lines.
