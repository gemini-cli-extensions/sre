# CHANGELOG

*   **1.0.8:** Simplified wrapper templating to use an explicit `PROJECT_ID="change-me"` pattern for better AI/human readability. Removed colloquialisms from setup script output.
*   **1.0.7:** Hardcoded `PROJECT_ID` into the generated `safe_gcloud` wrapper script. Moved changelog out of `SKILL.md` to reduce context bloat.
*   **1.0.6:** Replaced downloaded service account keys with secure service account impersonation to comply with common org policies.
*   **1.0.5:** Fixed invalid IAM role roles/security_reviewer to roles/iam.securityReviewer.
*   **1.0.4:** Updated email template to include dynamic gcloud commands for Option 1.
*   **1.0.3:** Handled IAM permission errors gracefully and added email_to_admin template.
*   **1.0.2:** Fixed missing line continuation backslashes in gcloud commands.
*   **1.0.1:** Added `safe_kubectl` wrapper and setup for read-only Kubernetes investigations. Added `roles/compute.networkViewer` to GCP roles.
*   **1.0.0:** Initial version with `safe_gcloud` setup and risk assessment.
