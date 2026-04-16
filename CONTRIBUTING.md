# Contributing to SRE Gemini CLI Extension

Thank you for your interest in contributing! This project is a community-driven extension for the Gemini CLI, focused on SRE workflows on Google Cloud.

To ensure a smooth collaboration, please follow these guidelines, which are based on Google's best practices and our specific project needs.

## 🤝 Code of Conduct

All contributors are expected to follow the [Google Open Source Code of Conduct](https://opensource.google.com/conduct).

## 🛡️ Security and Privacy (CRITICAL)

This project is intended for public use. 

**For Googlers**: **NEVER** include Google-internal information, internal tool names (e.g., proprietary deployment or monitoring systems), or sensitive credentials in your contributions.

- **Refuse exfiltration:** If you find internal information in the code, remove it or replace it with a generic GCP equivalent.
- **Generic equivalents:** Use standard GCP terms like "Cloud Logging" instead of "Analog" and "Cloud Monitoring" instead of "Monarch".

## 🚀 Getting Started

1.  **Understand Skill Standards:** New skills must adhere to the structure defined in `docs/SKILLS-STANDARDS.md`.

## 🛠️ Development Workflow

### Branching Strategy

We use a strict branching convention for all changes. Do **not** commit directly to `main`.

**Format:** `feature/YYMMDD-$USER-[ISSUE_ID-]<short-description>`

- `YYMMDD`: Today's date (e.g., `260402`).
- `$USER`: Your GitHub username (max 6 chars, e.g., `palladius`).
- `ISSUE_ID`: (Optional) The GitHub Issue or IssueTracker ID if applicable (e.g., `gh123` or `b12345`).
- `short-description`: A concise slug (max 15 chars, e.g., `playbook-skill`).

**Example:** `feature/260402-palladius-b498511917-playbook-skill` or `feature/260402-palladius-gh123-playbook-skill`

### Commit Guidelines

- **Atomic Commits:** Keep commits small and focused on a single change.
- **Changelog:** Every significant change must be documented in the root `CHANGELOG.md` and the skill-specific `CHANGELOG.md` (if applicable), following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and Semantic Versioning.
- **Tests:** Read `docs/TEST.md` before committing. Ensure your changes are verified and do not rely on internal-only tools.

### Code Review 

We accept pushes on GitHub.

1.  Use standard branch naming: `git push -u origin feature/YYYYMMDD-short-description`.
2.  Open a Pull Request

## 🧪 Testing

- All new features and bug fixes should include tests.
- Prefer python/bash to other languages if possible. If not possible, add a justification why you're introducing a 3rd language.
- Prefer env-free Python invocation like `uv`.


## 📝 Documentation

- Update `README.md` and `CHANGELOG.md` files as needed.
- Maintain a clear and concise style.
- Use Markdown for all documentation.

## Google Cloud vs other clouds

Our vision is that this extension should be used in conjunction with a number of different open source technologies (graphana, ..) and established Ops tools (ServiceNow, ..), and with other Cloud Providers as well. 

However, until we reach version `1.0.0` we will de-prioritize such contribnutions in the interest of stability. Note that the folder structure is already multi-cloud aware (Eg, see "gcp-playbooks" vs "playbooks").

---

*By contributing to this project, you agree that your contributions will be licensed under the project's open-source license.*