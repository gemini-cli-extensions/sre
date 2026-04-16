# Cloud Build Playbooks
API Name: `cloudbuild.googleapis.com`

If Cloud Build is used to push code to Artifact Repository and then to Cloud Run or GKE,
a good skill called "cloud-build-investigation" can be used to correlate code changes with failed builds.
This can be used to cross-correlate software and opertational errors thanks to the ltitle time delta between
a git commit/push and the operational trigger which results in a failure.

Note that the FIRST failure after N successes is usually the interesting one, and it can be often tracked down to the triggering cause (eg code push -> commit_id -> `git diff`).
