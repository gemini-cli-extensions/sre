<!--
  Some are Inspired by Romin: https://github.com/rominirani/google-mcp-servers/blob/main/prompts/getting-started.md
-->


## Logging

- Prompt: "Fetch the last 50 logs with a severity of 'ERROR' from Cloud Logging for this project."
- Test: Should use MCP to fetch the logs.

## Monitoring

- Prompt: "Show me all the currently active Cloud Monitoring alert policies so I can review our notification configurations."
- Test: Should use MCP to fetch the alert policies.

## GKE

- Prompt: "List all my GKE clusters across all regions, and tell me the current node count and Kubernetes version for each."
- Test: Should use MCP to fetch the GKE clusters.

## Run

- Prompt: "List all my Cloud Run services across all regions, and tell me the current CPU and memory allocation for each."
- Test: Should use MCP to fetch the Cloud Run services.

## DKP

- Prompt: "What does "ConnectionPoolExhausted: Unable to acquire aconnection from the pool within the timeout." error mean?"
- Test: Should use MCP to search for this in the DKP knowledge base.

## Good Skill Structure

<!-- Note: this should be available on EVERY skill, so this is the wrong place.-->

Input: this folder should have a SKILL.md and an EVAL.md file. The only allowed sub folders are references/ and scripts/.
Output: check `ls` and ensure it contains "SKILL.md" in the path.
