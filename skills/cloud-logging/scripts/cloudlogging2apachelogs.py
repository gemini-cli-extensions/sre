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

import json
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 cloudlogging2apachelogs.py <logfile.json>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        sys.exit(1)

    for entry in data:
        # Base fields
        timestamp = entry.get('timestamp', '-')
        
        # HTTP Request object
        http_req = entry.get('httpRequest', {})
        
        # Extracting specific fields with fallbacks
        ip = http_req.get('remoteIp', '-')
        method = http_req.get('requestMethod', '-')
        url = http_req.get('requestUrl', '-')
        protocol = http_req.get('protocol', 'HTTP/1.1')
        status = http_req.get('status', '-')
        size = http_req.get('responseSize', '-')
        user_agent = http_req.get('userAgent', '-')
        
        # Print loosely resembling Apache Combined Log format
        # IP - - [Timestamp] "METHOD URL PROTOCOL" STATUS SIZE "USER_AGENT"
        print(f'{ip} - - [{timestamp}] "{method} {url} {protocol}" {status} {size} "{user_agent}"')

if __name__ == "__main__":
    main()
