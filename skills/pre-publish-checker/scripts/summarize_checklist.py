#!/usr/bin/env python3
import sys
import os
import re

def summarize(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Checklist file '{file_path}' not found.")
        sys.exit(1)

    pending_files = []
    failed_files = []

    # Match markdown table rows like: | ./file.md | [Fail] | Reason |
    row_pattern = re.compile(r'^\|\s*(.*?)\s*\|\s*\[(.*?)\]\s*\|\s*(.*?)\s*\|')

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = row_pattern.match(line.strip())
            if match:
                filepath, status, reason = match.groups()
                
                # Skip the header separator line
                if '---' in filepath:
                    continue
                
                status_lower = status.strip().lower()
                if status_lower == 'pending':
                    pending_files.append(filepath.strip())
                elif status_lower == 'fail':
                    failed_files.append((filepath.strip(), reason.strip()))

    print(f"=== Publication Synopsis for '{file_path}' ===\n")
    
    if not failed_files and not pending_files:
        print("✅ All clear! No pending or failed items found. You are ready to publish.")
        return

    if failed_files:
        print(f"❌ FAILED CHECKS ({len(failed_files)}):")
        print("These items have flagged issues that need to be resolved or bypassed.")
        for fp, reason in failed_files:
            print(f"  - {fp}")
            print(f"    Reason: {reason}")
        print("")

    if pending_files:
        print(f"⏳ PENDING REVIEWS ({len(pending_files)}):")
        print("These items have not yet been evaluated.")
        for fp in pending_files:
            print(f"  - {fp}")
        print("")

if __name__ == "__main__":
    # Default to PUBLICATION_CHECKLIST.md if no argument is provided
    target_file = sys.argv[1] if len(sys.argv) > 1 else "PUBLICATION_CHECKLIST.md"
    summarize(target_file)
