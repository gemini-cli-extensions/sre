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
import sys
import os
import json
import unittest
import urllib.request
from unittest.mock import patch, MagicMock

# --- Utility Functions ---

def get_gcloud_identity():
    """Retrieves the current gcloud account email."""
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "account"],
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return "Unknown"

def get_adc_identity():
    """Retrieves the email associated with Application Default Credentials."""
    try:
        # Get ADC token
        token_res = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        token = token_res.stdout.strip()
        
        # Call tokeninfo to get the email
        req = urllib.request.Request(f"https://oauth2.googleapis.com/tokeninfo?access_token={token}")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("email", "Unknown")
    except Exception:
        return "Unknown (ADC not configured)"

def get_configured_servers():
    """Reads settings.json and returns a list of configured MCP server keys."""
    settings_paths = [
        os.path.join(os.getcwd(), ".gemini", "settings.json"),
        os.path.expanduser("~/.gemini/settings.json")
    ]
    configured = []
    for path in settings_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    configured.extend(data.get('mcpServers', {}).keys())
            except Exception:
                pass
    return list(set(configured))

def run_gemini_command(prompt):
    """Executes a gemini command in headless mode and returns the output."""
    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error running gemini: {str(e)}"

# --- Integration / Live System Checks ---

class TestOneMCPIntegration(unittest.TestCase):
    
    def test_identity_match(self):
        """Verifies that gcloud and ADC identities match."""
        print("\n[Security] Verifying identity consistency...")
        gcloud_id = get_gcloud_identity()
        adc_id = get_adc_identity()
        
        print(f"  gcloud identity: {gcloud_id}")
        print(f"  ADC identity:    {adc_id}")
        
        if gcloud_id != adc_id:
            self.fail(f"Identity mismatch! identity1 = {gcloud_id}, identity2 = {adc_id}. "
                      "Run 'gcloud auth application-default login' to fix.")
        print("  ✅ Identities match.")

    def test_mcp_list_output(self):
        """Verifies that /mcp list contains our expected OneMCP servers."""
        print("\n[Integration] Verifying MCP server configuration via Gemini CLI...")
        output = run_gemini_command("/mcp list")
        
        configured_servers = get_configured_servers()
        # Only check for google-managed ones
        expected_servers = [s for s in configured_servers if s.startswith("google-")]
        
        if not expected_servers:
            print("  ⚠️ No google-* MCP servers found in settings.json. Skipping list check.")
            return

        for server in expected_servers:
            with self.subTest(server=server):
                self.assertIn(server, output, f"MCP server '{server}' not found in /mcp list output")
                print(f"  ✅ Found {server}")

    def test_mcp_status_emojis(self):
        """Checks if servers are showing the green status emoji if connected."""
        output = run_gemini_command("/mcp list")
        
        if "🟢" in output or "Ready" in output or "Connected" in output:
            print("  ✅ Green status (🟢) or 'Ready' detected for at least one server!")
        else:
            print("  ⚠️ Note: Servers detected but none are currently 'Ready' (expected in headless CI).")

# --- Unit Tests for setup_onemcp.py logic ---

class TestOneMCPSetupLogic(unittest.TestCase):
    
    def test_missing_arguments(self):
        """Ensures the setup script fails correctly when no project_id or flags are provided."""
        script_path = os.path.join(os.path.dirname(__file__), "setup_onemcp.py")
        
        # Test 1: No arguments at all
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Script should fail with no arguments")
        self.assertIn("the following arguments are required", result.stderr)

        # Test 2: Project ID but no --local/--global flag
        result = subprocess.run([sys.executable, script_path, "test-project"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "Script should fail without mandatory scope flag")
        self.assertIn("one of the arguments --local --global is required", result.stderr)

    def test_help_output(self):
        """Verifies that --help works and contains expected flags."""
        script_path = os.path.join(os.path.dirname(__file__), "setup_onemcp.py")
        result = subprocess.run([sys.executable, script_path, "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--local", result.stdout)
        self.assertIn("--global", result.stdout)
        self.assertIn("--google-maps-key", result.stdout)

def get_kubectl_context():
    """Retrieves current kubectl context and user from config."""
    try:
        res = subprocess.run(
            ["kubectl", "config", "view", "--minify", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(res.stdout)
        contexts = data.get("contexts", [])
        if contexts:
            return contexts[0].get("context", {}).get("user", "Unknown")
        return "No context"
    except Exception:
        return "Unknown (kubectl error)"

def get_kubectl_whoami():
    """Retrieves current kubectl authenticated identity from the server."""
    try:
        res = subprocess.run(
            ["kubectl", "auth", "whoami", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(res.stdout)
        # Kubernetes 1.25+ returns json with status fields
        username = data.get("status", {}).get("userInfo", {}).get("username", "Unknown")
        groups = data.get("status", {}).get("userInfo", {}).get("groups", [])
        return username, groups
    except Exception:
        # Fallback to non-json parsing if -o json is not supported or fails
        try:
            res = subprocess.run(
                ["kubectl", "auth", "whoami"],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse table output
            lines = res.stdout.strip().split("\n")
            username = "Unknown"
            groups = []
            for line in lines:
                if "Username" in line:
                    username = line.split()[-1]
                elif "Groups" in line:
                    # Groups can be a list or comma separated
                    groups = line.split()[-1:]
            return username, groups
        except Exception:
            return "Unknown (kubectl auth error)", []

class TestKubectlIntegration(unittest.TestCase):
    
    def test_kubectl_context(self):
        """Checks if kubectl workspace context is set and running."""
        print("\n[Kubernetes] Verifying kubectl context...")
        user = get_kubectl_context()
        real_user, groups = get_kubectl_whoami()
        print(f"  kubectl config user/context: {user}")
        print(f"  kubectl server authenticated user: {real_user}")
        print(f"  kubectl groups: {groups}")
        
        if "Unknown" in user or "Unknown" in real_user:
            print("  ⚠️ Warning: kubectl context or auth seems unconfigured or errored.")
            print("  💡 Suggestion: Run 'gcloud container clusters get-credentials online-boutique --region=us-central1 --project=YOUR_PROJECT'")

if __name__ == "__main__":
    # If run with --unittest, execute the unit tests and integration tests
    if len(sys.argv) > 1 and sys.argv[1] == "--unittest":
        unittest.main(argv=[sys.argv[0]])
    else:
        # Simple execution mode (original behavior)
        print("Starting OneMCP Verification...")
        
        gcloud_id = get_gcloud_identity()
        adc_id = get_adc_identity()
        kubectl_user = get_kubectl_context()
        
        if gcloud_id != adc_id:
            print(f"\n❌ Error: Identity mismatch detected!")
            print(f"   - gcloud identity (CLI): {gcloud_id}")
            print(f"   - ADC identity (MCP):    {adc_id}")
            print(f"\n💡 Path Forward:")
            print(f"   Your MCP servers use Application Default Credentials (ADC), while your CLI uses gcloud login.")
            print(f"   To synchronize them, please run the following command in your terminal:")
            print(f"\n   gcloud auth application-default login --account={gcloud_id}\n")
            # sys.exit(1) # Don't exit early, let's check kubectl too!
        
        print("\n--- Kubernetes Setup ---")
        real_user, groups = get_kubectl_whoami()
        print(f"  kubectl config user:             {kubectl_user}")
        print(f"  kubectl server authenticated as: {real_user}")
        print(f"  kubectl groups:                  {groups}")
        
        if "Unknown" in kubectl_user or "Unknown" in real_user:
            print("  ❌ Error: kubectl context or auth seems unconfigured or errored.")
            print("  👉 Suggestion: Run 'gcloud container clusters get-credentials online-boutique --region=us-central1 --project=YOUR_PROJECT'\n")
        else:
            print("  ✅ kubectl configured.")

        output = run_gemini_command("/mcp list")
        print("\n--- Gemini Output ---")
        print(output)
        print("----------------------\n")
        
        configured_servers = get_configured_servers()
        expected = [s for s in configured_servers if s.startswith("google-")]

        all_found = True
        for s in expected:
            if s in output:
                # Check for 🟢 indicator in a simple way
                status = "🟢" if "🟢" in output and s in output else "⚪"
                print(f"{status} {s}: Found")
            else:
                print(f"❌ {s}: MISSING")
                all_found = False
        
        if not all_found:
            sys.exit(1)
        print("\nVerification Successful!")
