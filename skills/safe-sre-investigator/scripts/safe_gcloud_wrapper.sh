#!/bin/bash

# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Wrapper for gcloud to use the safe-sre-investigator service account via impersonation.

# Note to AI/User: Substitute 'change-me' with the actual GCP Project ID during setup.
PROJECT_ID="change-me" 

if [ "${PROJECT_ID}" == "change-me" ] || [ -z "${PROJECT_ID}" ]; then
  # Fallback: expect the project ID as the first argument
  PROJECT_ID="$1"
  shift 
fi

if [ -z "${PROJECT_ID}" ]; then
  echo "Error: Project ID is required." >&2
  echo "Usage: safe_gcloud <project-id> [gcloud commands]" >&2
  exit 1
fi

SA_EMAIL="safe-sre-investigator@${PROJECT_ID}.iam.gserviceaccount.com"

# Check if called with no gcloud commands, if so, just print info
if [ $# -eq 0 ]; then
    echo "safe_gcloud wrapper: Activated for project '${PROJECT_ID}' using impersonation with SA '${SA_EMAIL}'"
    echo "Usage: safe_gcloud [gcloud commands]"
    echo "Example: safe_gcloud compute instances list"
    exit 0
fi

# Run the gcloud command using Service Account Impersonation
gcloud --impersonate-service-account="${SA_EMAIL}" --project="${PROJECT_ID}" "$@"

