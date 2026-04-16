<p align="center">
  <img src="docs/sre-extension-logo.png" width="400" alt="SRE Extension Logo">
</p>

# About

**The SRE Gemini CLI Extension** is a dedicated toolkit comprising specialized **Skills** designed to augment Site Reliability Engineers (SREs). By integrating deeply with the Gemini CLI, this extension empowers SREs to investigate outages, configure MCP servers, formulate mitigations, and detect anomalies more rapidly.

## INSTALL

* You need [Gemini CLI installed](https://geminicli.com/).
* Then type:

```bash
gemini extensions install https://github.com/gemini-cli-extensions/sre
```


## Available Skills

### 🛠️ Core SRE Skills
- **`investigation-entrypoint`**: Primary entrypoint for investigating production outages, orchestrating SRE response, and mitigating incidents. Start here when an incident occurs!
- **`gcp-playbooks`**: Follows established SRE playbooks for GCP/GKE investigations, including infrastructure discovery and common mitigation steps.
- **`gcp-mcp-setup`**: Automates enabling services, Google Managed MCP (OneMCP) servers, generating API keys, and configuring `~/.gemini/settings.json`.
- **`gcp-slo-management`**: Discover Monitoring Services, list existing SLOs, or create new SLOs (Availability/Latency) via the REST API.
- **`postmortem-generator`**: Creates a generated PostMortem given enough context about a resolved incident/outage.

### ☁️ Cloud Capabilities
- **`cloud-build-investigation`**: Expert-level SRE skill for Google Cloud Build (GCB) and Cloud Run investigations. Correlates git commits with build failures and analyzes logs.
- **`cloud-logging`**: Skill for interacting with and analyzing Google Cloud Logging and Error Reporting. Processes large JSON logs or converts them to Apache format.
- **`cloud-monitoring`**: Interacts with Google Cloud Monitoring via APIs to avoid large context bloat. Exports time-series data and helps setup SLOs.

### 📊 Detection, Graphs & Mitigations
- **`generic-mitigations`**: Generic Mitigations high-level classification logic and actuation plan.
- **`monitoring-graphs`**: Generates high-quality, annotated incident graphs for post-mortems using Python to visualize outages and error rates (nice graphs visible [here](https://github.com/palladius/about-sre-extension/)).
- **`anomaly-detection`**: Detects anomalies in time-series data from various sources (Isolation Forest, KNN, Z-score).
- **`data-ingestion`**: Fetches and parses time-series data from various sources for downstream analysis.

> [!WARNING]
> The **`safe-sre-investigator`** skill is deprecated and has been merged into native playbooks.

## Quickstart

1. Install this extension via the Gemini CLI's install command:
   `gemini extensions install https://github.com/gemini-cli-extensions/sre`
2. Only for the first time, use `gcp-mcp-setup` skill to setup your GCP project, and MCP servers:
   ```bash
   $ gemini 
   Use the gcp-mcp-setup skill to setup my GCP project "foo-bar-123" with email jane-doe-sre@credible-company.com 
   ```
2. Invoke the entrypoint skill with your incident request. For example:
   ```bash 
   $ gemini
   Invoke the investigation entrypoint skill with this new incident: cluster gKE with ip 1.2.3.4 is reported down by numerous customers, please investigate.
   ```
3. The agent will take it from there—fetching context, querying metrics, and formulating mitigations.

For detailed instructions on setup and usage, please refer to the [User Manual](USER_MANUAL.md).


## Contributing

Check `CONTRIBUTING.md`.



## Feedback 

For feedback, please report **bugs** and **feature requests** in the issue tracker.
Any other intelligible feedback should be sent to this form: [SRE Extension Survey](https://forms.gle/eJPrbG4KKESp6GmF6)

# Thanks

Program Lead: [Riccardo](https://github.com/palladius)

Co-authors and contributors:
- [Madhavi](https://github.com/madkarra)
- [Ramón](https://github.com/rmedranollamas)
- [Szymon](https://github.com/szymonst)
<!-- add your name here -->
