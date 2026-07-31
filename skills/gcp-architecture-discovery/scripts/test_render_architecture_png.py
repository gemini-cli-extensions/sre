#!/usr/bin/env python3
import os
import tempfile
import unittest
import json
import subprocess
import sys

# Add the script directory to the path so we can import the render script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from render_architecture_png import render_graphviz_to_png

class TestRenderArchitecturePNG(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.valid_dot = "digraph G { A -> B; }"
        
        # Check if dot is installed, otherwise skip tests that run it
        try:
            subprocess.run(['dot', '-V'], capture_output=True, check=True)
            self.dot_installed = True
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.dot_installed = False

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_json_extraction(self):
        if not self.dot_installed:
            self.skipTest("Graphviz 'dot' command not installed.")
            
        json_path = os.path.join(self.temp_dir.name, "test.json")
        with open(json_path, 'w') as f:
            json.dump({"graphviz": self.valid_dot}, f)
            
        try:
            render_graphviz_to_png(json_path)
            out_png = os.path.join(self.temp_dir.name, "test.png")
            self.assertTrue(os.path.exists(out_png))
            self.assertGreater(os.path.getsize(out_png), 0)
        except SystemExit as e:
            self.fail(f"render_graphviz_to_png exited unexpectedly with code {e.code}")

    def test_md_extraction(self):
        if not self.dot_installed:
            self.skipTest("Graphviz 'dot' command not installed.")
            
        md_path = os.path.join(self.temp_dir.name, "test.md")
        with open(md_path, 'w') as f:
            f.write(f"Some text\n```graphviz\n{self.valid_dot}\n```\nMore text")
            
        try:
            render_graphviz_to_png(md_path)
            out_png = os.path.join(self.temp_dir.name, "test.png")
            self.assertTrue(os.path.exists(out_png))
            self.assertGreater(os.path.getsize(out_png), 0)
        except SystemExit as e:
            self.fail(f"render_graphviz_to_png exited unexpectedly with code {e.code}")

    def test_missing_file(self):
        with self.assertRaises(SystemExit) as cm:
            render_graphviz_to_png("nonexistent_file.json")
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
