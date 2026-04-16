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

import os
import sys
from pathlib import Path

def is_executable(path):
    return os.access(path, os.X_OK) and not os.path.isdir(path)

def main():
    root_dir = Path(__file__).parent.parent
    skills_dir = root_dir / "skills"
    
    if not skills_dir.exists():
        print(f"Error: {skills_dir} not found.")
        sys.exit(1)

    allowed_extensions = {".py", ".sh"}
    # Files to ignore even if they might be executable or in a scripts/ directory
    ignored_extensions = {".md", ".json", ".csv", ".png", ".jpg", ".jpeg", ".txt", ".sample", ".yaml", ".yml", ".svg", ".png", ".md"}
    
    total_errors = 0
    
    for root, dirs, files in os.walk(skills_dir):
        current_dir = Path(root)
        
        # Rule 0: Folder names should not end with 'copy'
        if current_dir.name.lower().endswith('copy') or current_dir.name.lower().endswith('-copy'):
            relative_path = current_dir.relative_to(root_dir)
            print(f"FAIL: {relative_path}")
            print(f"  [ERROR] Folder name '{current_dir.name}' ends with 'copy'. Please ASK OWNER to reconcile with original and rename folder.")
            total_errors += 1

        is_in_scripts_dir = current_dir.name == "scripts"
        
        for file in files:
            file_path = current_dir / file
            ext = file_path.suffix.lower()
            
            if ext in ignored_extensions:
                continue

            error_found = False
            
            # Rule 1: All potential scripts in a 'scripts' directory must be .py or .sh
            if is_in_scripts_dir:
                if ext not in allowed_extensions:
                    error_found = True
            
            # Rule 2: All executable files must be .py or .sh
            elif is_executable(file_path):
                if ext not in allowed_extensions:
                    error_found = True
            
            if error_found:
                relative_path = file_path.relative_to(root_dir)
                print(f"FAIL: {relative_path}")
                print("  [ERROR] All scripts should be in bash or python")
                total_errors += 1

    if total_errors == 0:
        print("All scripts in skills validated successfully.")
        sys.exit(0)
    else:
        print(f"\nValidation complete: {total_errors} errors found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
