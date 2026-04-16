
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
import yaml
import re
import sys
import argparse
from pathlib import Path

def validate_semantic_version(version):
    return re.match(r'^\d+\.\d+\.\d+$', str(version)) is not None

def validate_name_format(name):
    return re.match(r'^[a-z0-9-]+$', str(name)) is not None

def check_skill_frontmatter(file_path, verbose=False):
    errors = []
    warnings = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return ["No valid YAML frontmatter found (missing --- markers)"], []
        
        frontmatter_raw = match.group(1)
        try:
            data = yaml.safe_load(frontmatter_raw)
        except yaml.YAMLError as ye:
            return [f"YAML Parsing Error: {str(ye)}"], []
        
        if not data:
            return ["Frontmatter is empty or invalid YAML"], []

        # MANDATORY (Error)
        mandatory_fields = ['name', 'description']
        for field in mandatory_fields:
            if field not in data:
                errors.append(f"Missing mandatory field: '{field}'")
        
        # SHOULD (Warning)
        if 'metadata' not in data:
            warnings.append("Missing field: 'metadata' (SHOULD have it)")
        else:
            metadata = data['metadata']
            if not isinstance(metadata, dict):
                errors.append("'metadata' should be a dictionary")
            else:
                if 'author' not in metadata:
                    warnings.append("Missing field in metadata: 'author' (SHOULD have it)")
                if 'version' not in metadata:
                    warnings.append("Missing field in metadata: 'version' (SHOULD have it)")
                else:
                    if not validate_semantic_version(metadata['version']):
                        errors.append(f"Invalid version format: '{metadata['version']}'. Use semantic versioning (e.g., 0.0.1)")

                # OPTIONAL (Warning if --verbose)
                if 'status' not in metadata:
                    if verbose:
                        warnings.append("Missing field in metadata: 'status' (optional)")
                else:
                    status = metadata['status']
                    allowed_statuses = ['draft', 'needs-review', 'published']
                    if status not in allowed_statuses:
                        errors.append(f"Invalid status: '{status}'. Allowed: {', '.join(allowed_statuses)}")

        # Validate 'name' format and consistency
        if 'name' in data:
            name = data['name']
            if not validate_name_format(name):
                errors.append(f"Invalid name format: '{name}'. Use dashes, no spaces, lowercase.")
            
            if str(name).lower().endswith('copy') or str(name).lower().endswith('-copy'):
                errors.append(f"Skill name '{name}' ends with 'copy'. Please reconcile with original and remove 'copy' suffix.")
            
            folder_path = Path(file_path).parent
            folder_name = folder_path.name

            is_copy = folder_name.lower().endswith('copy') or folder_name.lower().endswith('-copy')

            if name != folder_name and not is_copy:
                errors.append(f"Skill name '{name}' does not match folder name '{folder_name}'")
            
            if not validate_name_format(folder_name):
                errors.append(f"Invalid folder name format: '{folder_name}'. Use dashes, no spaces, lowercase (no underscores).")
            
            if is_copy:
                errors.append(f"Folder name '{folder_name}' ends with 'copy'. Please ASK OWNER to reconcile with original and rename folder.")

        # Validate 'description' starts with dragon
        if 'description' in data:
            description = str(data['description']).strip()
            if not description.startswith('🐉'):
                errors.append("Description must start with the dragon emoji '🐉'")

    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
    
    return errors, warnings

def find_skill_files(search_dirs):
    skill_files = []
    seen_inodes = set()
    for d in search_dirs:
        if not d.exists(): continue
        for root, dirs, files in os.walk(d, followlinks=True):
            if "SKILL.md" in files:
                full_path = Path(root) / "SKILL.md"
                try:
                    inode = full_path.stat().st_ino
                    if inode not in seen_inodes:
                        seen_inodes.add(inode)
                        skill_files.append(full_path)
                except FileNotFoundError: continue
    return skill_files

def main():
    parser = argparse.ArgumentParser(description="Check skills frontmatter for compliance.")
    parser.add_argument("--verbose", action="store_true", help="Show optional warnings.")
    parser.add_argument("--no-warnings", action="store_true", help="Do not show warning messages.")
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent
    search_dirs = [root_dir / "skills", root_dir / ".gemini" / "skills"]
    skill_files = find_skill_files(search_dirs)
    
    if not skill_files:
        print("No SKILL.md files found.")
        return

    total_errors = 0
    total_warnings = 0
    for skill_file in skill_files:
        try: relative_path = skill_file.relative_to(root_dir)
        except ValueError: relative_path = skill_file
            
        errors, warnings = check_skill_frontmatter(skill_file, verbose=args.verbose)
        if errors or (warnings and not args.no_warnings):
            status = "FAIL" if errors else "WARN"
            print(f"{status}: {relative_path}")
            for error in errors:
                print(f"  [ERROR] {error}")
            if not args.no_warnings:
                for warning in warnings:
                    print(f"  [WARN]  {warning}")
            total_errors += len(errors)
            total_warnings += len(warnings)
        else:
            if args.verbose:
                print(f"PASS: {relative_path}")

    if not args.verbose and total_errors == 0 and total_warnings == 0:
        print("All skills frontmatter validated successfully.")
    elif total_errors > 0 or total_warnings > 0:
        print(f"\nValidation complete: {total_errors} errors, {total_warnings} warnings.")
    
    if total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
