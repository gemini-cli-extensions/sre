#!/usr/bin/env bash
#
# Prints the version from a JSON manifest file.
# Prints "version missing" if the file does not exist, version key is absent, or on error.

set -euo pipefail

FILEPATH="${1:-}"

if [ -z "$FILEPATH" ]; then
    echo "Usage: $0 <path-to-json-file>" >&2
    exit 1
fi

if [ -f "$FILEPATH" ]; then
    # Try using jq if available
    if command -v jq >/dev/null 2>&1; then
        VERSION=$(jq -r .version "$FILEPATH" 2>/dev/null || echo "version missing")
        if [ "$VERSION" = "null" ]; then
            VERSION="version missing"
        fi
        echo "$VERSION"
    else
        # Basic grep fallback if jq is missing
        VERSION=$(grep -o '"version": "[^"]*' "$FILEPATH" 2>/dev/null | cut -d'"' -f4 || echo "version missing")
        if [ -z "$VERSION" ]; then
            VERSION="version missing"
        fi
        echo "$VERSION"
    fi
else
    echo "version missing"
fi
