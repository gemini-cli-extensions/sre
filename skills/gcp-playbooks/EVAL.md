# Evaluation: GCP Playbooks Skill

This file tracks the evaluation metrics and scenarios for the `gcp-playbooks` skill.

## Scenarios

1. **New Project Discovery**: A user asks the agent to investigate a project it has never seen before.
2. **Mitigation Search**: A user asks for a specific mitigation (e.g., "how do I rollback a Cloud Run service?").

## Metrics

- **Recall**: Proportion of relevant playbooks found for a given scenario.
- **Accuracy**: Proportion of gcloud/kubectl commands that are correct and executable.
- **Completeness**: Proportion of relevant infrastructure components correctly identified.
