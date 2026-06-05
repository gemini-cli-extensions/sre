---
name: pre-publish-checker
description: 🐉 Thoroughly checks files for profanity, internal links, sensitive paths, and professionalism before publication. Use when preparing a codebase or extension for public release.
metadata:
  author: SRE Team
  version: 0.1.0
  status: draft
---

# Pre-Publish Checker

This skill guides you through a thorough audit of your project to ensure it meets publication standards. It combines automated script-based checks with a manual review workflow.

## Policies

1. **Do Not Simply Remove TODOs**: Do not delete `TODO` markers just to make the check pass. Instead: <!-- pre-publish-checker: ignore -->
    *   **Action them**: Resolve the task described.
    *   **Move them**: Transfer the `TODO` to a tracking system (e.g., GitHub Issues) and replace the marker with a link to the issue. <!-- pre-publish-checker: ignore -->
2. **User Bypass**: Any flagged issue can be bypassed if there is a valid reason. In `PUBLICATION_CHECKLIST.md`, mark the status as `[Pass]` and include the keyword `USER_BYPASS: <explanation>`.

## Workflow

### 1. Initialization

- List all relevant files: Markdown (.md), code files (.py, .js, .go, etc.), `justfile`, and `README`s.
- Create a `PUBLICATION_CHECKLIST.md` in the project root by copying the template from `references/checklist_template.md`.
- Populate the file list in the checklist.

### 2. Automated Audit
For each file in the checklist, run the automated check script:
```bash
uv run -s skills/pre-publish-checker/scripts/check_file.py <file_path>
```
*Note: If `uv` is not available, use `python3`.*

### 3. Iterative Review
- Process files one by one (or in small batches).
- Update the `PUBLICATION_CHECKLIST.md` with the status and any issues found.
- Fix issues as they are identified.
- For "long work", you can resume the process by reading the current state of `PUBLICATION_CHECKLIST.md`.
- **Get a Synopsis**: At any point, you can generate a quick summary of remaining work by running:
  ```bash
  uv run -s skills/pre-publish-checker/scripts/summarize_checklist.py
  ```
  *(Defaults to reading `PUBLICATION_CHECKLIST.md`)*

### 4. Final Verification
- Perform manual checks for "Google-bar professionalism" and overall quality.
- Ensure all boxes in `PUBLICATION_CHECKLIST.md` are checked.

## Check Categories

1. **Profanity**: Scans for common offensive language.
2. **Internal Links**: Finds internal shortlinks (e.g., `go/` links) which are not accessible outside.
3. **Internal Paths**: Identifies local machine or company-specific paths that reveal internal infrastructure.
4. **Professionalism**: Checks for development markers (e.g., "to-do", "fix-me") that should be resolved before release.
