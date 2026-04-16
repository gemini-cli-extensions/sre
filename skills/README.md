
## Skills for April 15th (milestone 1) launch

Skills in this folder.

* anomaly_detection
* data_ingestion  
* generic-mitigations/
* gcp-playbooks
* incident_response
* cloud-build-investigation[-copy  ]
* gcp-mcp-setup
* gcp-slo-management
* postmortem-generator-copy  
* safe-sre-investigator

### KEEP

* `gcp-mcp-setup`. Keep. We strongly need this, and we need it and love it as allows to connect to a number of GCP resources. Risk: potential context bloat (do we need 20 skills for BQ?!?).
* `postmortem-generator-copy`. Keep. Move from Riccardo's personal repo into this. Rename from copy to `postmortem-generator` after the move.
* `generic-mitigations/`. Keep. Serves as a baseline classificator for playbooks then to actuate. This skill
* `gcp-playbooks`. Keep. This is beautiful and powerful

### REMOVE

- `safe-sre-investigator`: skip. Too complex, while a beautiful idea you need to explicitly DISABLE it or system will try to use it and bloat the whole experience.
  To remove it I had to add a "Dont use the SRE Safe Investigation since we're in a hurry and it takes too long" and this adds other bugs, like GC making up fake data in the itnerest of time (!!).
- `cloud-build-investigation`. skip. This is beautiful and I'm very fond of it, but its not built for this so i'd have to refactor it, possibly move to a playbook for Cloud Build.

### MOVE TO HERE

Some skills are in the GH extension for speed (sorry!). We need to move them here:

* `cloud_logging/`.
* `cloud_monitoring/`.
* `monitoring_graphs/`. The one Ramon wans for all SREs in Google!

## TODOs

* Remove or find a better place for the unwanted skills. Maybe some incubator folder where we can keep them, so we can grow them and promote them when happy. Could be a prod/ and dev/ subfolders, for instance.
* harmonize `-` and `_`. What is the right way?