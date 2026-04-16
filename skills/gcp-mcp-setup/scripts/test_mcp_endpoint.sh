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

# test_mcp_endpoint.sh
# Direct verification of OneMCP endpoints using curl to list tools.

# GEMINI: Keep these Sorted!
KNOWN_ENDPOINTS=(
    "https://aiplatform.googleapis.com/mcp"
    "https://bigquery.googleapis.com/mcp"
    "https://clouderrorreporting.googleapis.com/mcp"
    "https://cloudresourcemanager.googleapis.com/mcp"
    "https://compute.googleapis.com/mcp"
    "https://container.googleapis.com/mcp"
    "https://developerknowledge.googleapis.com/mcp"
    "https://firestore.googleapis.com/mcp"
    "https://logging.googleapis.com/mcp"
    "https://monitoring.googleapis.com/mcp"
    "https://pubsub.googleapis.com/mcp"
    "https://run.googleapis.com/mcp"
    "https://spanner.googleapis.com/mcp"
    "https://sqladmin.googleapis.com/mcp"
)

ENDPOINT=$1

if [ -z "$ENDPOINT" ]; then
    echo "💡 No endpoint provided. Usage: $0 <ENDPOINT_URL>"
    echo "Available known endpoints:"
    for ep in "${KNOWN_ENDPOINTS[@]}"; do
        echo "  - $ep"
    done
    exit 0
fi

echo "🔍 Fetching tools from: $ENDPOINT"
echo "--------------------------------------------------"

# Fetch tools and extract names one per line
curl --silent --location "$ENDPOINT" \
--header 'content-type: application/json' \
--header 'accept: application/json, text/event-stream' \
--data '{
    "method": "tools/list",
    "jsonrpc": "2.0",
    "id": 1
}' | jq -r '.result.tools[].name' || echo "❌ Error: Failed to query endpoint or parse JSON."

echo "--------------------------------------------------"
