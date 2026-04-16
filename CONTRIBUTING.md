# Contributing to SRE Gemini CLI Extension

Thank you for your interest in contributing! This project is a community-driven extension for the Gemini CLI, focused on SRE workflows on Google Cloud.

This document includes:

- **[Before you begin](#before-you-begin):** Essential steps before contributing.
- **[Code contribution process](#code-contribution-process):** How to contribute code and skills.
- **[Testing](#testing):** Requirements for verifying changes.
- **[Documentation contribution process](#documentation-contribution-process):** How to contribute to the project's documentation.
- **[Google Cloud vs other clouds](#google-cloud-vs-other-clouds):** Our project vision.

---

## Before you begin

### Sign our Contributor License Agreement

Contributions to this project must be accompanied by a [Contributor License Agreement](https://cla.developers.google.com/about) (CLA). You (or your employer) retain the copyright to your contribution; this simply gives us permission to use and redistribute your contributions as part of the project.

Visit <https://cla.developers.google.com/> to sign or verify your agreements.

### Review our Community Guidelines

This project follows [Google's Open Source Community Guidelines](https://opensource.google/conduct/).

### Getting started

1.  **Find an issue** that you want to work on.
2.  **Fork the repository** and create a new branch.
3.  **Understand Skill Standards:** New skills must adhere to the structure defined in `docs/SKILLS-STANDARDS.md`.

### Forking

If you are forking the repository, you will be able to run the Build and Test workflows. In order to make the integration tests run, you'll need to add a [GitHub Repository Secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) with a value of `GEMINI_API_KEY` and set that to a valid API key. Your key and secret are private to your repo.

Additionally, you will need to click on the `Actions` tab and enable workflows for your repository.

### Branching Strategy

We use a strict branching convention for all changes. Do **not** commit directly to `main`.

**Format:** `feature/YYMMDD-$USER-[ISSUE_ID-]<short-description>`

- `YYMMDD`: Today's date (e.g., `260402`).
- `$USER`: Your GitHub username (max 6 chars, e.g., `palladi`).
- `ISSUE_ID`: (Optional) The GitHub Issue or IssueTracker ID if applicable (e.g., `gh123` or `123`).
- `short-description`: A concise slug (max 15 chars, e.g., `playbook-skill`).

**Example:** `feature/260402-palladi-123-playbook-skill`

### Pull request guidelines

To help us review and merge your PRs quickly, please follow these guidelines:

1.  **Link to an existing issue:** All PRs should be linked to an existing issue. This ensures the change is aligned with project goals.
2.  **Keep it small and focused:** We favor small, atomic PRs. Break down large changes into a series of smaller, logical PRs.
3.  **Atomic Commits:** Keep commits small and focused on a single change.
4.  **Clear Titles and Messages:** Use descriptive PR titles and follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.
    - **Good:** `feat(skill): add cloud-sql-troubleshooter`
    - **Bad:** `Update skill`
5.  **Changelog:** Every significant change must be documented in the root `CHANGELOG.md` and the skill-specific `CHANGELOG.md` (if applicable), following [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Testing

- All new features and bug fixes should include tests.
- **Language Preference:** Prefer Python or Bash for tests. If introducing a new language, please provide a justification.
- **Sandboxing:** Read `docs/TEST.md` before committing. Ensure your changes do not rely on internal-only tools or network access that won't be available in public environments.

## Documentation contribution process

Our documentation must be kept up-to-date with our code contributions. We value clarity, accuracy, and completeness.

1.  **Preview changes:** Preview your markdown changes locally before submitting.
2.  **Style:** Use sentence case for headings, write in the second person ("you"), and use present tense.
3.  **Examples:** Provide practical examples to help users understand how to use the extension or specific skills.

## Google Cloud vs other clouds

Our vision is that this extension should be used in conjunction with various open-source technologies (Grafana, etc.) and established Ops tools (ServiceNow, etc.), and eventually other Cloud Providers. 

However, until we reach version `1.0.0`, we will prioritize GCP-focused contributions in the interest of stability. Note that the folder structure is already multi-cloud aware (e.g., `gcp-playbooks` vs `playbooks`).

---

*By contributing to this project, you agree that your contributions will be licensed under the project's open-source license.*
