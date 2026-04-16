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

# gcp-whoami.sh: Neatly display 3 GCP identities.

# 1. gcloud Current Identity
GCLOUD_ACCOUNT=$(gcloud config get-value account 2>/dev/null)
GCLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null)
echo "1. [gcloud] Active Account: ${GCLOUD_ACCOUNT:-'N/A'}"
if [ -n "$GCLOUD_PROJECT" ]; then
    echo "            Project ID:     $GCLOUD_PROJECT"
fi

# 2. ADC (Application Default Credentials) Identity
ADC_EMAIL=$(curl -s -H "Authorization: Bearer $(gcloud auth application-default print-access-token 2>/dev/null)" \
  https://www.googleapis.com/oauth2/v1/userinfo 2>/dev/null | grep email | cut -d'"' -f4)
echo "2. [ADC]    Active Identity: ${ADC_EMAIL:-'N/A'}"

ADC_PROJECT=${GOOGLE_CLOUD_PROJECT:-""}
if [[ "$ADC_EMAIL" == *".iam.gserviceaccount.com" ]]; then
    ADC_PROJECT=$(echo "$ADC_EMAIL" | awk -F'@' '{print $2}' | cut -d'.' -f1)
fi

if [ -z "$ADC_PROJECT" ]; then
    if [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ] && [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        ADC_PROJECT=$(grep -m1 '"project_id"' "$GOOGLE_APPLICATION_CREDENTIALS" 2>/dev/null | cut -d'"' -f4)
    elif [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
        ADC_PROJECT=$(grep -m1 '"quota_project_id"' "$HOME/.config/gcloud/application_default_credentials.json" 2>/dev/null | cut -d'"' -f4)
    fi
fi

if [ -n "$ADC_PROJECT" ]; then
    echo "            Project ID:     $ADC_PROJECT"
else
    echo "            Project ID:     N/A (No quota project or env set)"
fi

# 3. Kubernetes (GKE) Identity
if command -v kubectl &> /dev/null; then
    K8S_USER=$(kubectl auth whoami --output json 2>/dev/null | jq -r '.status.userInfo.username' 2>/dev/null)
    # Fallback if jq is not available or whoami output is not json-friendly
    if [ -z "$K8S_USER" ] || [ "$K8S_USER" == "null" ]; then
        K8S_USER=$(kubectl auth whoami 2>/dev/null | grep Username | awk '{print $2}')
    fi
    echo "3. [K8S]    Active Identity: ${K8S_USER:-'N/A'}"
    
    K8S_CONTEXT=$(kubectl config current-context 2>/dev/null)
    if [ -n "$K8S_CONTEXT" ]; then
        K8S_CLUSTER=$(kubectl config view --minify -o jsonpath='{.contexts[0].context.cluster}' 2>/dev/null)
        K8S_NS=$(kubectl config view --minify -o jsonpath='{.contexts[0].context.namespace}' 2>/dev/null)
        K8S_NS=${K8S_NS:-"default"}
        
        if [[ "$K8S_CLUSTER" == gke_* ]]; then
            GKE_PROJECT=$(echo "$K8S_CLUSTER" | cut -d'_' -f2)
            GKE_CLUSTER_NAME=$(echo "$K8S_CLUSTER" | cut -d'_' -f4)
            echo "            Cluster Name:    $GKE_CLUSTER_NAME"
            echo "            GKE Project:     $GKE_PROJECT"
            echo "            kubectl config:  $K8S_CONTEXT"
        else
            echo "            Context:         $K8S_CONTEXT"
            if [ "$K8S_CONTEXT" != "$K8S_CLUSTER" ]; then
                echo "            Cluster:         $K8S_CLUSTER"
            fi
        fi

        if [ "$K8S_NS" != "default" ]; then
            echo "            Namespace:       $K8S_NS"
        fi
    fi
else
    echo "3. [K8S]    kubectl not installed."
fi
