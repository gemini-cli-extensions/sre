# Email Template for IAM Admin

If you encountered a "Policy update access denied" error when setting up the Safe SRE Investigator, you can send this email to your GCP Project Admin.

---

**Subject:** Request for Safe SRE Investigator access on project ${PROJECT_ID}

Hi Admin,

I am setting up a read-only "Safe SRE Investigator" service account to help me debug issues safely without risking accidental changes to production. 

Could you please do one of the following?

**Option 1: Temporarily grant me permission to set it up myself**
Please grant me the `roles/resourcemanager.projectIamAdmin` role on project `${PROJECT_ID}`.

For a temporary 1-hour grant (recommended), you can run:
```bash
# Note: You can adjust the expiration timestamp as needed.
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="user:${USER_EMAIL}" \
    --role="roles/resourcemanager.projectIamAdmin" \
    --condition="expression=request.time < timestamp(\"$(date -u -d '+1 hour' +'%Y-%m-%dT%H:%M:%SZ')\"),title=Temporary SRE Setup Access,description=One-hour temporary access for Safe SRE Investigator setup"
```

For a permanent grant:
```bash
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="user:${USER_EMAIL}" \
    --role="roles/resourcemanager.projectIamAdmin"
```

**Option 2: Create the Service Account and grant the roles for me**
Please run the following gcloud commands to create the service account and assign the read-only roles (this is safe and only grants viewer access):

```bash
export PROJECT_ID="${PROJECT_ID}"
export SA_EMAIL="safe-sre-investigator@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create safe-sre-investigator \
  --display-name="Safe SRE Investigator" \
  --description="Read-only access for SRE investigations" \
  --project "${PROJECT_ID}"

for role in roles/viewer roles/iam.securityReviewer roles/logging.viewer roles/monitoring.viewer roles/browser roles/container.viewer roles/compute.viewer roles/storage.objectViewer roles/run.viewer roles/monitoring.dashboardEditor; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${role}" \
    --condition=None
done

# Grant me impersonation rights on the Service Account
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="user:${USER_EMAIL}" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project="${PROJECT_ID}"
```

Thanks!
