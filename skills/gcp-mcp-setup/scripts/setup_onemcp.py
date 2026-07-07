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

"""
OneMCP Setup Script
This script sets the gcloud project, installs beta components, enables required services
and MCP servers.

By default, it installs a lean SRE toolset (Logging, Monitoring, GKE, Run, RM, ErrorReporting, DK).
Use --all to include databases (SQL, Spanner, Firestore, BigQuery) and Vertex AI.

Use --harness to target a specific CLI harness (gemini, antigravity, copilot).
Defaults to gemini+antigravity when omitted.

# Thanks to Romin Irani guidance: https://github.com/rominirani/google-mcp-servers/blob/main/demos/README.md
"""

import argparse
import subprocess
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from harness_registry import HARNESS_REGISTRY, HarnessName

# On Windows, the default encoding is cp1252 which cannot encode emojis. Use UTF-8 to avoid encoding errors.
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')


def run_command(command, check=True):
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, text=True, encoding='utf-8', capture_output=True, shell=(sys.platform == "win32"))
    if check and result.returncode != 0:
        print(f"Command failed with error: {result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    return result

def main():
    parser = argparse.ArgumentParser(
        description="Set up Google Managed MCP (OneMCP) for your CLI harness."
    )
    parser.add_argument("project_id", help="The Google Cloud Project ID to use.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--local", action="store_true", help="Update the local config file (workspace-scoped).")
    group.add_argument("--global", action="store_true", dest="global_config", help="Update the global config file (user-scoped).")

    parser.add_argument(
        "--harness",
        choices=[h.value for h in HarnessName],
        default=None,
        help="Target CLI harness to configure (gemini, antigravity, copilot). Defaults to gemini+antigravity.",
    )
    parser.add_argument("--all", action="store_true", help="Enable all supported OneMCP servers, including databases and Vertex AI.")
    parser.add_argument("--google-maps-key", dest="google_maps_key", help="The Google Maps API Key to enable mapstools MCP.")

    args = parser.parse_args()
    project_id = args.project_id
    scope = "local" if args.local else "global"

    # Resolve target harnesses: explicit selection or default to gemini+antigravity.
    if args.harness:
        selected_harnesses = [args.harness]
    else:
        selected_harnesses = [HarnessName.GEMINI, HarnessName.ANTIGRAVITY]

    # Resolve target config files from the registry.
    target_files = []
    for harness in selected_harnesses:
        harness_config = HARNESS_REGISTRY[harness]
        for path in harness_config.paths(scope):
            resolved = os.path.expanduser(path) if path.startswith("~") else os.path.join(os.getcwd(), path)
            target_files.append((resolved, harness_config.builder))

    # Core SRE Services (Default)
    base_services = [
        "logging.googleapis.com",
        "monitoring.googleapis.com",
        "container.googleapis.com",
        "run.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        # "developerknowledge.googleapis.com"
    ]

    # Extra Services (Enabled with --all)
    extra_services = [
        "clouderrorreporting.googleapis.com",
        "sqladmin.googleapis.com",
        "spanner.googleapis.com",
        "pubsub.googleapis.com",
        "aiplatform.googleapis.com",
        "firestore.googleapis.com",
        "bigquery.googleapis.com"
    ]

    if args.all:
        base_services.extend(extra_services)
    
    if args.google_maps_key:
        base_services.append("mapstools.googleapis.com")

    print(f"Setting project to {project_id}...")
    run_command(["gcloud", "config", "set", "project", project_id])

    print("Installing beta components...")
    run_command(["gcloud", "components", "install", "beta", "--quiet"], check=False)

    print(f"Enabling {len(base_services)} services...")
    run_command(["gcloud", "services", "enable"] + base_services)

    print("Enabling Managed MCP servers...")
    for service in base_services:
        result = run_command(["gcloud", "beta", "services", "mcp", "enable", service], check=False)
        if result.returncode != 0:
            print(f"Failed to enable {service} MCP or already enabled")

    print("Creating Developer Knowledge API Key...")
    display_name = f"Developer Knowledge Key {int(time.time())}"
    result = run_command([
        "gcloud", "services", "api-keys", "create", 
        f"--project={project_id}", 
        f"--display-name={display_name}", 
        "--format=value(response.keyString)"
    ])
    dev_key = result.stdout.strip()

    # Map service names to MCP config keys and URLs
    mcp_config_map = {
        'logging.googleapis.com': ('google-logging', 'https://logging.googleapis.com/mcp'),
        'monitoring.googleapis.com': ('google-monitoring', 'https://monitoring.googleapis.com/mcp'),
        'container.googleapis.com': ('google-container', 'https://container.googleapis.com/mcp'),
        'run.googleapis.com': ('google-run', 'https://run.googleapis.com/mcp'),
        'cloudresourcemanager.googleapis.com': ('google-resourcemanager', 'https://cloudresourcemanager.googleapis.com/mcp'),
        'clouderrorreporting.googleapis.com': ('google-errorreporting', 'https://clouderrorreporting.googleapis.com/mcp'),
        'compute.googleapis.com': ('google-compute', 'https://compute.googleapis.com/mcp'), # Added check just in case
        'sqladmin.googleapis.com': ('google-sql', 'https://sqladmin.googleapis.com/mcp'),
        'spanner.googleapis.com': ('google-spanner', 'https://spanner.googleapis.com/mcp'),
        'pubsub.googleapis.com': ('google-pubsub', 'https://pubsub.googleapis.com/mcp'),
        'aiplatform.googleapis.com': ('google-vertexai', 'https://aiplatform.googleapis.com/mcp'),
        'firestore.googleapis.com': ('google-firestore', 'https://firestore.googleapis.com/mcp'),
        'bigquery.googleapis.com': ('google-bigquery', 'https://bigquery.googleapis.com/mcp'),
    }

    def build_mcp_servers(builder):
        servers = {}
        for service in base_services:
            if service == 'developerknowledge.googleapis.com':
                servers['google-developer-knowledge'] = builder(
                    'https://developerknowledge.googleapis.com/mcp', api_key=dev_key
                )
            elif service == 'mapstools.googleapis.com':
                servers['google-maps'] = builder(
                    'https://mapstools.googleapis.com/mcp', api_key=args.google_maps_key
                )
            elif service in mcp_config_map:
                key, url = mcp_config_map[service]
                servers[key] = builder(url, project_id=project_id)
        return servers

    for config_file, builder in target_files:
        print(f"Updating {config_file}...")
        os.makedirs(os.path.dirname(config_file), exist_ok=True)

        data = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {config_file} contains invalid JSON. Overwriting.")

        if 'mcpServers' not in data:
            data['mcpServers'] = {}

        data['mcpServers'].update(build_mcp_servers(builder))

        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Successfully updated {config_file} with OneMCP servers.")
    print("\n======================================================")
    print(f"OneMCP Setup Complete for project: {project_id}")
    print(f"Services Enabled: {', '.join(base_services)}")
    print("======================================================")

if __name__ == "__main__":
    main()
