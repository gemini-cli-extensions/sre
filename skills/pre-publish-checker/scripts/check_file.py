#!/usr/bin/env python3
import sys
import re
import os

# Basic list of common profanities (to be expanded if needed)
PROFANITY_LIST = [
    r'\bshit\b', r'\bfuck\b', r'\bdamn\b', r'\bass\b', r'\bbitch\b'
]

# Patterns for internal links and paths
INTERNAL_PATTERNS = [
    (r'\bgo/[a-zA-Z0-9\-/]+\b', "Internal go/ link found"),
    (r'/google/', "Internal /google/ path found"),
    (r'/usr/local/google/', "Internal /usr/local/google/ path found"),
]

def check_file(file_path):
    issues = []
    if not os.path.exists(file_path):
        return [f"File not found: {file_path}"]
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.splitlines()

            for i, line in enumerate(lines):
                if 'pre-publish-checker: ignore' in line:
                    continue
                line_no = i + 1

                # 1. Profanity check
                for pattern in PROFANITY_LIST:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        issues.append(f"Line {line_no}: Potential profanity found: '{match.group()}'")

                # 2. Internal links and paths
                for pattern, message in INTERNAL_PATTERNS:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        issues.append(f"Line {line_no}: {message}: '{match.group()}'")

                # 3. Professionalism (TODO, FIXME, etc.)
                prof_patterns = [
                    (r'\bTODO\b', "TODO found"),
                    (r'\bFIXME\b', "FIXME found"),
                    (r'\bHACK\b', "HACK found"),
                    (r'\bXXX\b', "XXX found"),
                ]
                for pattern, message in prof_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        issues.append(f"Line {line_no}: {message}")

    except Exception as e:
        return [f"Error reading file: {str(e)}"]

    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check_file.py <file_path>")
        sys.exit(1)

    file_to_check = sys.argv[1]
    results = check_file(file_to_check)
    
    if results:
        print(f"Issues found in {file_to_check}:")
        for issue in results:
            print(f"  - {issue}")
    else:
        print(f"No issues found in {file_to_check}.")
