#!/usr/bin/env python3

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

import subprocess
import json
import argparse
import sys

def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

def get_token():
    token_cmd = ["gcloud", "auth", "application-default", "print-access-token"]
    token_res = subprocess.run(token_cmd, capture_output=True, text=True)
    if token_res.returncode != 0:
        print("❌ Error: Failed to get ADC token. Run 'gcloud auth application-default login'.")
        sys.exit(1)
    return token_res.stdout.strip()

def list_services(project_id):
    print(f"🔍 Fetching Monitoring Services for {project_id}...")
    token = get_token()
    url = f"https://monitoring.googleapis.com/v3/projects/{project_id}/services"
    curl_cmd = ["curl", "-s", "-H", f"Authorization: Bearer {token}", url]
    
    data = run_command(curl_cmd)
    if not data or 'services' not in data:
        print("No services found.")
        return

    print(f"{'Display Name':<25} | {'Service ID':<60}")
    print("-" * 90)
    for svc in data['services']:
        full_name = svc['name']
        short_id = full_name.split('/')[-1]
        print(f"{svc.get('displayName', 'N/A'):<25} | {short_id:<60}")

def list_slos(project_id, service_id):
    print(f"🔍 Fetching SLOs for Service: {service_id}...")
    token = get_token()
    url = f"https://monitoring.googleapis.com/v3/projects/{project_id}/services/{service_id}/serviceLevelObjectives"
    curl_cmd = ["curl", "-s", "-H", f"Authorization: Bearer {token}", url]
    
    data = run_command(curl_cmd)
    if not data or 'serviceLevelObjectives' not in data:
        print("No SLOs found for this service.")
        return

    print(f"{'Display Name':<40} | {'Goal':<10} | {'Period':<15}")
    print("-" * 75)
    for slo in data['serviceLevelObjectives']:
        goal = slo.get('goal', 'N/A')
        period = slo.get('rollingPeriod', 'N/A')
        print(f"{slo.get('displayName', 'N/A'):<40} | {goal:<10} | {period:<15}")

def main():
    parser = argparse.ArgumentParser(description="Discover Monitoring Services and SLOs")
    parser.add_argument("project_id", help="GCP Project ID")
    parser.add_argument("--service-id", help="List SLOs for a specific Service ID")
    args = parser.parse_args()

    if args.service_id:
        list_slos(args.project_id, args.service_id)
    else:
        list_services(args.project_id)

if __name__ == "__main__":
    main()
