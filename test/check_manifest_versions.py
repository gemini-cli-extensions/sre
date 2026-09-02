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

import json
import sys
from pathlib import Path

def main():
    root_dir = Path(__file__).parent.parent
    
    manifest_paths = [
        root_dir / "gemini-extension.json",
        root_dir / "plugin.json",
        root_dir / ".claude-plugin/plugin.json",
        root_dir / ".codex-plugin/plugin.json",
    ]
    
    versions = {}
    total_errors = 0
    
    for path in manifest_paths:
        if not path.exists():
            print(f"FAIL: {path.relative_to(root_dir)} does not exist.")
            total_errors += 1
            continue
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            version = data.get("version")
            if not version:
                print(f"FAIL: {path.relative_to(root_dir)} is missing 'version' field.")
                total_errors += 1
            else:
                versions[path.relative_to(root_dir)] = version
        except Exception as e:
            print(f"FAIL: Failed to parse {path.relative_to(root_dir)}: {e}")
            total_errors += 1
            
    if total_errors > 0:
        sys.exit(1)
        
    unique_versions = set(versions.values())
    
    if len(unique_versions) > 1:
        print("FAIL: Version mismatch found between manifest files:")
        for rel_path, ver in versions.items():
            print(f"  {rel_path}: {ver}")
        sys.exit(1)
    elif len(unique_versions) == 1:
        version = list(unique_versions)[0]
        print(f"Success: All {len(versions)} manifest files are in sync at version {version}.")
        sys.exit(0)
    else:
        print("FAIL: No manifest files found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
