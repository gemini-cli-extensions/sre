#!/usr/bin/env python3
"""
Utility script to render Mermaid.js diagrams from a Markdown file to a PNG image.
Uses external mermaid.ink API. Safe for non-confidential architecture graphs.
"""
import base64
import json
import re
import sys
import urllib.request
import zlib
import os

def render_mermaid_to_png(md_path):
    if not os.path.exists(md_path):
        print(f"Error: File {md_path} not found.")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract mermaid block
    match = re.search(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
    if not match:
        print(f"No Mermaid block found in {md_path}. Skipping PNG generation.")
        sys.exit(0)

    mermaid_code = match.group(1).strip()
    
    # Encode to base64 for mermaid.ink
    # mermaid.ink expects base64 encoded string of the diagram or json state
    encoded = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
    
    api_url = f"https://mermaid.ink/img/{encoded}"
    out_png_path = os.path.splitext(md_path)[0] + '.png'
    
    print(f"Rendering diagram to {out_png_path}...")
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 SRE-Bot/1.0'})
        with urllib.request.urlopen(req) as response, open(out_png_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Successfully generated {out_png_path}")
    except Exception as e:
        print(f"Failed to render diagram: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_architecture_png.py <path_to_architecture.md>")
        sys.exit(1)
    render_mermaid_to_png(sys.argv[1])
