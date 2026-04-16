#!/usr/bin/env -S uv run

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

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "google-api-python-client",
#     "google-auth",
#     "python-dateutil",
# ]
# ///

"""
Pending approval from its author), the one and only Wietse Venema.

USER MANUAL:
This script correlates Google Cloud Run Revisions with Google Cloud Error Reporting data.
It helps you determine exactly which revision of a Cloud Run service contains or introduced specific errors.

Usage:
  ./tmp_weitse_pending_approval.py --project <PROJECT_ID> --region <REGION> --service <SERVICE_NAME> --days <DAYS>

Arguments:
  --project, -p   The Google Cloud Project ID.
  --region, -r    The Cloud Run region (e.g., europe-west1).
  --service, -s   The Cloud Run service name.
  --days, -d      Number of days to look back for errors (e.g., 1, 7, 30).

Example:
  ./tmp_weitse_pending_approval.py -p my-gcp-project -r us-central1 -s my-backend-service -d 7

What it does:
1. Connects to the GCP Cloud Run API to fetch revision history for the given service.
2. Connects to the GCP Error Reporting API to fetch error groups within the specified timeframe.
3. Matches specific error events to the Cloud Run revision version they occurred in.
4. Outputs an easy-to-read list of revisions, marking them as ✅ CLEAN or ❌ <N> Error Types Found.
5. Provides a detailed stacktrace and GCP console link for each error group found.
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
import google.auth
from dateutil import parser

def get_cloud_run_revisions(project_id, region, service_name):
    """
    Fetches Cloud Run revisions for the given service.
    """
    credentials, _ = google.auth.default()
    service = build('run', 'v1', credentials=credentials)
    parent = f"projects/{project_id}/locations/{region}"
    
    print(f"Fetching Cloud Run revisions for {service_name} in {region}...")
    
    revisions = []
    try:
        # We assume managed Cloud Run (v1 API)
        request = service.projects().locations().revisions().list(
            parent=parent,
            labelSelector=f"serving.knative.dev/service={service_name}"
        )
        response = request.execute()
        
        items = response.get('items', [])
        for item in items:
            metadata = item.get('metadata', {})
            name = metadata.get('name')
            creation_timestamp = metadata.get('creationTimestamp')
            
            if name and creation_timestamp:
                revisions.append({
                    'name': name,
                    'created': creation_timestamp,
                })
                
    except Exception as e:
        print(f"Warning: Could not fetch Cloud Run revisions: {e}")
        
    return revisions

def get_errors_by_revision(project_id, region, service_name, days):
    """
    Fetches error groups and aggregates them by Cloud Run revision.
    """
    credentials, _ = google.auth.default()
    service = build('clouderrorreporting', 'v1beta1', credentials=credentials)
    
    project_name = f"projects/{project_id}"
    
    print(f"Fetching error groups for {project_id} (last {days} days)...")
    
    # Map days to closest allowed period
    if days <= 1:
        period = "PERIOD_1_DAY"
    elif days <= 7:
        period = "PERIOD_1_WEEK"
    else:
        period = "PERIOD_30_DAYS"

    response = None
    try:
        response = service.projects().groupStats().list(
            projectName=project_name,
            timeRange_period=period
        ).execute()
    except Exception as e:
        print(f"Error fetching group stats: {e}")
        
    group_stats = response.get('errorGroupStats', []) if response else []
    
    # Structure: revision -> list of error details
    revision_errors = defaultdict(list)
    
    # Global map of group_id -> error details to print at the end
    all_error_groups = {}

    if group_stats:
        print(f"Found {len(group_stats)} error groups. Analyzing affected revisions...")
        
        for stat in group_stats:
            group_id = stat['group']['groupId']
            count = stat['count']
            message = stat['representative']['message']
            last_seen = stat['lastSeenTime']
            
            # Fetch specific events to find the revision ID
            try:
                events_response = service.projects().events().list(
                    projectName=project_name,
                    groupId=group_id,
                    pageSize=10
                ).execute()
                
                events = events_response.get('errorEvents', [])
                seen_revisions_for_group = set()
                
                for event in events:
                    context = event.get('serviceContext', {})
                    version = context.get('version')
                    
                    if version:
                        # Store global error details
                        if group_id not in all_error_groups:
                            request_context = event.get('context', {}).get('httpRequest', {})
                            method = request_context.get('method', 'N/A')
                            url = request_context.get('url', 'N/A')
                            
                            lines = message.strip().split('\n')
                            summary = lines[-1] if lines else "Unknown Error"
                            if len(lines) > 1 and lines[0].startswith("Traceback"):
                                    summary = lines[-1]
                            
                            if len(summary) > 100:
                                summary = summary[:97] + "..."

                            all_error_groups[group_id] = {
                                'summary': summary,
                                'full_message': message,
                                'group_id': group_id,
                                'method': method,
                                'url': url,
                                'affected_revisions': set()
                            }
                        
                        all_error_groups[group_id]['affected_revisions'].add(version)

                        if version not in seen_revisions_for_group:
                            seen_revisions_for_group.add(version)
                            revision_errors[version].append({
                                'group_id': group_id,
                                'summary': all_error_groups[group_id]['summary'],
                                'event_time': event['eventTime']
                            })
            except Exception as e:
                print(f"Warning: Could not fetch events for group {group_id}: {e}")
    else:
        if response:
             print("No errors found in the specified period.")

    # Fetch Revisions
    all_revisions = get_cloud_run_revisions(project_id, region, service_name)
    
    all_revisions.sort(key=lambda x: parser.parse(x['created']))
    
    window_end = datetime.now(timezone.utc)
    window_start = window_end - timedelta(days=days)
    
    relevant_revisions = []
    
    for i, rev in enumerate(all_revisions):
        created = parser.parse(rev['created'])
        if created.tzinfo is None:
             created = created.replace(tzinfo=timezone.utc)

        if i + 1 < len(all_revisions):
            next_created = parser.parse(all_revisions[i+1]['created'])
            if next_created.tzinfo is None:
                next_created = next_created.replace(tzinfo=timezone.utc)
            ended = next_created
        else:
            ended = window_end
            
        if created < window_end and ended > window_start:
            relevant_revisions.append(rev)
            
    relevant_revisions.sort(key=lambda x: parser.parse(x['created']), reverse=True)
    
    print("\n" + "="*80)
    print(f"REVISION OVERVIEW (Last {days} Days)")
    print("="*80 + "\n")
    
    displayed_revs = set()

    for rev in relevant_revisions:
        rev_name = rev['name']
        displayed_revs.add(rev_name)
        created = rev['created']
        errors = revision_errors.get(rev_name, [])
        
        print(f"Revision: {rev_name}")
        print(f"Created:  {created}")
        
        if not errors:
            print("Status:   ✅ CLEAN")
        else:
            print(f"Status:   ❌ {len(errors)} Error Types Found")
            errors.sort(key=lambda x: parser.parse(x['event_time']), reverse=True)
            for err in errors:
                print(f"  - [{err['group_id']}] {err['summary']}")
        print("-" * 40)

    orphaned_revs = [r for r in revision_errors.keys() if r not in displayed_revs]
    if orphaned_revs:
        print("\n[Other Revisions with Errors in this Period]")
        for rev_name in orphaned_revs:
            print(f"Revision: {rev_name}")
            errors = revision_errors[rev_name]
            print(f"Status:   ❌ {len(errors)} Error Types Found")
            for err in errors:
                print(f"  - [{err['group_id']}] {err['summary']}")
            print("-" * 40)

    if all_error_groups:
        print("\n" + "="*80)
        print("DETAILED ERROR LIST")
        print("="*80 + "\n")
        
        for group_id, details in all_error_groups.items():
            console_url = f"https://console.cloud.google.com/errors/{group_id}?project={project_id}"
            
            print(f"Error Group: {group_id}")
            print(f"Summary:     {details['summary']}")
            print(f"Method/URL:  {details['method']} {details['url']}")
            print(f"Affected:    {', '.join(details['affected_revisions'])}")
            print(f"Link:        {console_url}")
            print("Stack Trace:")
            for line in details['full_message'].split('\n'):
                print(f"  {line}")
            print("-" * 80)

if __name__ == "__main__":
    usage_examples = """
Usage examples:
  ./scripts/admin/report_errors_by_revision.py --project my-project --region europe-west1 --service my-service --days 7
  ./scripts/admin/report_errors_by_revision.py -p my-project -r europe-west1 -s my-service -d 3
"""
    arg_parser = argparse.ArgumentParser(
        description="Report errors by Cloud Run revision.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=usage_examples
    )
    arg_parser.add_argument("--project", "-p", required=True, help="Google Cloud Project ID")
    arg_parser.add_argument("--region", "-r", required=True, help="Cloud Run region (e.g., europe-west1)")
    arg_parser.add_argument("--service", "-s", required=True, help="Cloud Run service name")
    arg_parser.add_argument("--days", "-d", type=int, required=True, help="Number of days to look back")
    
    if len(sys.argv) == 1:
        arg_parser.print_help()
        sys.exit(1)

    args = arg_parser.parse_args()
    
    get_errors_by_revision(args.project, args.region, args.service, args.days)