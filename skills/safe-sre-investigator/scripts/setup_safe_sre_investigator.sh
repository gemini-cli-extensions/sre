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

# Sets up the safe-sre-investigator service account and a wrapper script.

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <PROJECT_ID>"
  exit 1
fi

PROJECT_ID="$1"
SA_EMAIL="safe-sre-investigator@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="${HOME}/.config/gcloud/safe-sre-investigator-${PROJECT_ID}-key.json"
WRAPPER_DIR="${HOME}/bin"
WRAPPER_PATH="${WRAPPER_DIR}/safe_gcloud"

# Determine the path to the template in the skill directory early
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ROLES_FILE="${SKILL_DIR}/references/iam_roles.txt"

if [ -f "$ROLES_FILE" ]; then
  echo "📖 Reading IAM roles from: ${ROLES_FILE}"
  # Read roles file, ignoring comments (#) and empty lines
  mapfile -t IAM_ROLES < <(grep -v '^#' "$ROLES_FILE" | sed '/^[[:space:]]*$/d')
else
  echo "⚠️ roles.txt not found, falling back to defaults..."
  IAM_ROLES=(
    "roles/viewer"
    "roles/iam.securityReviewer"
    "roles/logging.viewer"
    "roles/monitoring.viewer"
    "roles/browser"
    "roles/container.viewer"
    "roles/compute.viewer"
    "roles/storage.objectViewer"
    "roles/run.viewer"
    "roles/monitoring.dashboardEditor"
  )
fi

echo "🚀 Setting up safe-sre-investigator for project: ${PROJECT_ID}"

SUDO_GCLOUD="gcloud"
if ! gcloud config get-value project > /dev/null 2>&1; then
    echo "🤔 gcloud not initialized. Please run: gcloud init"
    exit 1
fi
gcloud config set project ${PROJECT_ID} > /dev/null

# 1. Create Service Account if it doesn't exist
if ! ${SUDO_GCLOUD} iam service-accounts describe "${SA_EMAIL}" --project "${PROJECT_ID}" > /dev/null 2>&1; then
  echo "✨ Creating Service Account: ${SA_EMAIL}"
  if ! ${SUDO_GCLOUD} iam service-accounts create safe-sre-investigator \
    --display-name="Safe SRE Investigator" \
    --description="Read-only access for SRE investigations" \
    --project "${PROJECT_ID}" 2>/tmp/sa_error.log; then
      echo "❌ Permission Denied: You do not have the required permissions to create it as you don't have powers."
      echo "Here are two possibilities:"
      echo "1. Ask your admin to temporarily give you 'resourcemanager.projectIamAdmin' (maybe expiring in 1 hour)."
      echo "2. Give your Admin the commands to create the service account for you."
      echo "👉 Please check the template email to your Admin:"
      echo "   cat ${SKILL_DIR}/references/email_to_admin.md"
      exit 1
  fi
else
  echo "✅ Service Account ${SA_EMAIL} already exists."
fi

# 2. Grant IAM Roles
echo "🔑 Granting IAM Roles..."
for role in "${IAM_ROLES[@]}"; do
  echo "  - ${role}"
  if ! ${SUDO_GCLOUD} projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${role}" \
    --condition=None > /dev/null 2> /tmp/iam_error.log; then
      if grep -q "Policy update access denied" /tmp/iam_error.log || grep -q "PERMISSION_DENIED" /tmp/iam_error.log; then
        echo "❌ Permission Denied: You do not have the required permissions to assign roles as you don't have IAM powers (resourcemanager.projects.setIamPolicy)."
        echo "Here are two possibilities:"
        echo "1. Ask your admin to temporarily give you 'resourcemanager.projectIamAdmin' (maybe expiring in 1 hour)."
        echo "2. Give your Admin the commands to grant the roles for you."
        echo "👉 Please check the template email to your Admin:"
        echo "   cat ${SKILL_DIR}/references/email_to_admin.md"
        exit 1
      else
        cat /tmp/iam_error.log
        exit 1
      fi
  fi
done
echo "✅ IAM roles granted."

# 3. Grant Service Account Token Creator role for Impersonation
CURRENT_USER=$(gcloud config get-value account 2>/dev/null)
echo "🔐 Granting Impersonation rights to ${CURRENT_USER} on ${SA_EMAIL}..."
if ! ${SUDO_GCLOUD} iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="user:${CURRENT_USER}" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project="${PROJECT_ID}" > /dev/null 2> /tmp/iam_error2.log; then
    if grep -q "Policy update access denied" /tmp/iam_error2.log || grep -q "PERMISSION_DENIED" /tmp/iam_error2.log; then
      echo "❌ Permission Denied: You do not have the required permissions to assign the impersonation role to yourself on the Service Account."
      echo "Give your Admin the commands to grant the roles for you."
      echo "👉 Please check the template email to your Admin:"
      echo "   cat ${SKILL_DIR}/references/email_to_admin.md"
      exit 1
    else
      cat /tmp/iam_error2.log
      exit 1
    fi
else
  echo "✅ Impersonation rights granted."
fi

# 4. Create safe_gcloud wrapper script
echo "📝 Creating wrapper script: ${WRAPPER_PATH}"
mkdir -p "${WRAPPER_DIR}"

TEMPLATE_PATH="${SKILL_DIR}/scripts/safe_gcloud_wrapper.sh"

if [ ! -f "${TEMPLATE_PATH}" ]; then
    echo "❌ Error: Wrapper template not found at ${TEMPLATE_PATH}" >&2
    exit 1
fi

cp "${TEMPLATE_PATH}" "${WRAPPER_PATH}"
sed -i "s/PROJECT_ID=\"change-me\"/PROJECT_ID=\"${PROJECT_ID}\"/g" "${WRAPPER_PATH}"
chmod +x "${WRAPPER_PATH}"

echo "✅ Wrapper script created."

# 5. Check if WRAPPER_DIR is in PATH
if [[ ":${PATH}:" != *":${WRAPPER_DIR}:"* ]]; then
  echo "⚠️ Warning: '${WRAPPER_DIR}' is not in your PATH."
  echo "  Please add it to your shell profile (e.g., ~/.bashrc, ~/.zshrc):"
  echo "    export PATH=\"${WRAPPER_DIR}:\$PATH\""
  echo "  Then, reload your shell: source ~/.bashrc"
fi

echo "🎉 Setup complete for safe-sre-investigator!"
echo "  You can now use: safe_gcloud ${PROJECT_ID} <gcloud_command>"