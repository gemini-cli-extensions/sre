# IAM Roles for safe-sre-investigator SA

The following IAM roles are recommended for the `safe-sre-investigator` service account to provide broad read-only access for investigation purposes.

**Comprehensive Read-Only Roles:**

*   `roles/viewer`: Provides read access to most GCP resources.
*   `roles/security_reviewer`: Allows inspection of IAM policies and security configurations.
*   `roles/logging.viewer`: Full access to read logs.
*   `roles/monitoring.viewer`: Full access to read monitoring data.
*   `roles/browser`: Can browse the project structure.

**Service-Specific Read-Only Roles:**

*   `roles/container.viewer`: Read-only access to GKE resources.
*   `roles/compute.viewer`: Read-only access to Compute Engine resources.
*   `roles/compute.networkViewer`: Read-only access to Networking resources.
*   `roles/storage.objectViewer`: Read access to GCS objects.
*   `roles/bigquery.dataViewer`: Read access to BigQuery datasets.
*   `roles/cloudsql.viewer`: Read-only access to Cloud SQL instances.
*   `roles/run.viewer`: Read-only access to Cloud Run resources.

**Limited Mutate Permissions:**

*   `roles/monitoring.dashboardEditor`: Allows creating and editing Monitoring dashboards.

**Note:** This list can be adjusted based on the specific services used in the project. The principle is to grant the least privilege necessary for investigation.
