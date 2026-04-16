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

PROJECT_ID=$(gcloud config get project)
CLUSTER_NAME="online-boutique" # Updated to your Autopilot cluster

# 1. Clean up existing metrics to avoid "already exists" errors
echo "Cleaning up old metrics..."
# gcloud logging metrics delete frontend_total_requests --quiet 2>/dev/null
# gcloud logging metrics delete frontend_error_requests --quiet 2>/dev/null

echo "Creating Log-based Metrics for cluster: $CLUSTER_NAME..."

# 2. Create Total Requests Metric (Filtered to cluster)
gcloud logging metrics create frontend_total_requests \
    --description="Total requests for SLO" \
    --log-filter="resource.labels.pod_name:\"frontend\" AND resource.labels.cluster_name=\"$CLUSTER_NAME\"" 2>/dev/null || echo "Metric frontend_total_requests might already exist."

# 3. Create Bad Requests Metric (Filtered to cluster)
gcloud logging metrics create frontend_error_requests \
    --description="Error requests for SLO" \
    --log-filter="resource.labels.pod_name:\"frontend\" AND resource.labels.cluster_name=\"$CLUSTER_NAME\" AND (severity>=ERROR OR textPayload:\"http response code: 5\")" 2>/dev/null || echo "Metric frontend_error_requests might already exist."

echo "Waiting 10 seconds for metrics to propagate..."
sleep 10

# 4. Use the REST API to find the Monitoring Service ID for the frontend
echo "Discovering Service ID..."
TOKEN=$(gcloud auth application-default print-access-token)
SERVICES=$(curl -s -X GET \
  -H "Authorization: Bearer $TOKEN" \
  "https://monitoring.googleapis.com/v3/projects/$PROJECT_ID/services")

# Extract the service ID that matches 'frontend'
SERVICE_ID=$(echo $SERVICES | grep -o '"name": "projects/[^"]*/services/[^"]*frontend[^"]*"' | head -n 1 | cut -d '"' -f 4 | awk -F'/services/' '{print $2}')

if [ -z "$SERVICE_ID" ]; then
    echo "❌ Error: No 'frontend' Monitoring Service found in project $PROJECT_ID."
    exit 1
fi

echo "Found Service ID: $SERVICE_ID"

# 5. Create the SLO using the REST API
echo "Creating SLO via REST API..."
cat << EOF > slo_payload.json
{
  "displayName": "Frontend Availability (Bash Created)",
  "goal": 0.999,
  "rollingPeriod": "2419200s",
  "serviceLevelIndicator": {
    "requestBased": {
      "goodTotalRatio": {
        "totalServiceFilter": "metric.type=\"logging.googleapis.com/user/frontend_total_requests\" resource.type=\"global\"",
        "badServiceFilter": "metric.type=\"logging.googleapis.com/user/frontend_error_requests\" resource.type=\"global\""
      }
    }
  }
}
EOF

curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://monitoring.googleapis.com/v3/projects/$PROJECT_ID/services/$SERVICE_ID/serviceLevelObjectives" \
  -d @slo_payload.json

rm slo_payload.json

echo -e "\n✅ Success! Your SLO is now active."
echo "Note: It may take 5-10 minutes for the Error Budget to show a positive value."
