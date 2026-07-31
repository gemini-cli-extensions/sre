#!/usr/bin/env python3
"""
Utility script to render Graphviz diagrams from a Markdown/JSON file to a PNG image.
Uses local Graphviz 'dot' command for secure, offline rendering.
"""
import json
import re
import sys
import os
import subprocess

def render_graphviz_to_png(input_path):
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        sys.exit(1)

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # If it's a markdown file, extract dot/graphviz block.
    # If it's a JSON file, try to extract from a "graphviz" key.
    # Otherwise assume raw dot code.
    if input_path.endswith('.md'):
        match = re.search(r'```(?:dot|graphviz)\n(.*?)\n```', content, re.DOTALL)
        if not match:
            print(f"No Graphviz block found in {input_path}. Skipping PNG generation.")
            sys.exit(0)
        dot_code = match.group(1).strip()
    elif input_path.endswith('.json'):
        try:
            data = json.loads(content)
            dot_code = data.get('graphviz', '').strip()
            if not dot_code:
                print(f"No 'graphviz' key found in JSON {input_path}. Skipping.")
                sys.exit(0)
        except json.JSONDecodeError:
            print(f"Invalid JSON in {input_path}. Skipping.")
            sys.exit(1)
    else:
        dot_code = content.strip()
        # Remove dot markdown fence if accidentally included
        dot_code = re.sub(r'^```(?:dot|graphviz)\n', '', dot_code)
        dot_code = re.sub(r'\n```$', '', dot_code).strip()
    
    out_png_path = os.path.splitext(input_path)[0] + '.png'

    print(f"Rendering diagram to {out_png_path} using local Graphviz...")
    try:
        process = subprocess.run(
            ['dot', '-Tpng', '-o', out_png_path],
            input=dot_code.encode('utf-8'),
            capture_output=True,
            check=True
        )
        print(f"Successfully generated {out_png_path}")
    except FileNotFoundError:
        print("Error: 'dot' command not found. Please ensure Graphviz is installed.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Failed to render diagram (dot exited with error): {e.stderr.decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to render diagram: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_architecture_png.py <path_to_architecture.json|md>")
        sys.exit(1)
    render_graphviz_to_png(sys.argv[1])
