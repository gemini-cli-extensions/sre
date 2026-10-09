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
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from check_skills_frontmatter import check_skill_frontmatter


class TestCheckSkillsFrontmatter(unittest.TestCase):
    def _write_skill(self, tmpdir, folder_name, content):
        skill_dir = Path(tmpdir) / folder_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(content, encoding="utf-8")
        return skill_md

    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = self._write_skill(
                tmpdir,
                "generic-mitigations",
                "---\n"
                "name: generic-mitigations\n"
                "description: 🐉 Guidance on utilizing generic mitigations.\n"
                "metadata:\n"
                '  author: "[Ramón Medrano Llamas](https://github.com/rmedranollamas)"\n'
                "  version: 0.0.1\n"
                "  status: published\n"
                "---\n# Body\n",
            )
            errors, warnings = check_skill_frontmatter(skill_md)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_unquoted_bracket_in_name_fails_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = self._write_skill(
                tmpdir,
                "postmortem-generator",
                "---\n"
                "name: [SRE] postmortem-generator\n"
                "description: 🐉 [SRE] Creates a PostMortem.\n"
                "---\n# Body\n",
            )
            errors, _ = check_skill_frontmatter(skill_md)
            self.assertTrue(any("YAML Parsing Error" in e for e in errors), errors)

    def test_unquoted_markdown_link_in_author_fails_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = self._write_skill(
                tmpdir,
                "generic-mitigations",
                "---\n"
                "name: generic-mitigations\n"
                "description: 🐉 Guidance on utilizing generic mitigations.\n"
                "metadata:\n"
                "  author: [Ramón Medrano Llamas](https://github.com/rmedranollamas)\n"
                "  version: 0.0.1\n"
                "---\n# Body\n",
            )
            errors, _ = check_skill_frontmatter(skill_md)
            self.assertTrue(any("YAML Parsing Error" in e for e in errors), errors)

    def test_unquoted_colon_in_description_fails_yaml(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = self._write_skill(
                tmpdir,
                "my-skill",
                "---\n"
                "name: my-skill\n"
                "description: 🐉 SRE: Investigate production incidents.\n"
                "---\n# Body\n",
            )
            errors, _ = check_skill_frontmatter(skill_md)
            self.assertTrue(any("YAML Parsing Error" in e for e in errors), errors)

    def test_list_in_metadata_author_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = self._write_skill(
                tmpdir,
                "generic-mitigations",
                "---\n"
                "name: generic-mitigations\n"
                "description: 🐉 Guidance on utilizing generic mitigations.\n"
                "metadata:\n"
                "  author: [Ramón Medrano Llamas]\n"
                "  version: 0.0.1\n"
                "---\n# Body\n",
            )
            errors, _ = check_skill_frontmatter(skill_md)
            self.assertTrue(
                any("author" in e.lower() and "string" in e.lower() for e in errors),
                f"Expected error for list in metadata.author, got: {errors}",
            )

    def test_quoted_sre_in_name_fails_format(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = self._write_skill(
                tmpdir,
                "postmortem-aggregator",
                "---\n"
                'name: "[SRE] postmortem-aggregator"\n'
                "description: 🐉 To be used when you have a folder containing N Post Mortem files.\n"
                "metadata:\n"
                "  author: Riccardo Carlesso\n"
                "  version: 0.0.1\n"
                "---\n# Body\n",
            )
            errors, _ = check_skill_frontmatter(skill_md)
            self.assertTrue(
                any("Invalid name format" in e for e in errors),
                f"Expected Invalid name format error, got: {errors}",
            )

    def test_redundant_sre_bracket_in_description_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_md = self._write_skill(
                tmpdir,
                "postmortem-aggregator",
                "---\n"
                "name: postmortem-aggregator\n"
                'description: "🐉 [SRE] To be used when you have a folder containing N Post Mortem files."\n'
                "metadata:\n"
                "  author: Riccardo Carlesso\n"
                "  version: 0.0.1\n"
                "---\n# Body\n",
            )
            errors, _ = check_skill_frontmatter(skill_md)
            self.assertTrue(
                any("[SRE]" in e for e in errors),
                f"Expected error for redundant [SRE] tag in description, got: {errors}",
            )


if __name__ == "__main__":
    unittest.main()

