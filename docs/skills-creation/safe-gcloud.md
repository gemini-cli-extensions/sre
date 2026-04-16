Use skill-creator skill to create a skill to do the following:

1. Setup or ensure existing servicve account called "safe-sre-investigator" exists in the project. tghis should have IAM permissions to do the following:

- READ any possible configuration
- SEE without MODIFYING production (Network, GKE, Compute, Storage, etc.), Logging, Monitoring, ...
- we might occasionally need to with some actions, like "create/mutate a dashboard".
- Create a "safe_gcloud" shell script which is a wrapper around gcloud which uses the service account above. This is becasue we migh have somne other person doing `gcloud auth login` and forget you have superpowers we want to avoid this.
- This should set up as a thing which takes 5-10min the first time but then its quite immediate and transparent in user experience. Not sure how to guarantee that :)
- NO WRITE ACCESS whatsoever to GKE, CRun, and so on. Although it should be able to SUGGEST commands for the user to run, like "to fix this, do <gcloud command>" or "<kubectl ..>".
- We'll set up a number of safe activities to run.

## Risk assessment

When suggesting user to execute a command, a risk assessment with emoji will be added something like this:

```bash
# 🎬 ACTION performed in English (or local language)
# ⚠️ Risk: <BALL EMOJI> [HIGH|MEDIUM|LOW|NONE]: <short explanation of the risk>. Ball emojise should be respectively red, yellow, green, white.
shell command to execute
```

Some examples:

```bash
# 🎬Drain cluster in europe-west1
# ⚠️ Risk: 🔴 HIGH: This command will drain the cluster, which may cause some services to be unavailable.
kubectl drain <node> --ignore-daemonsets
```

```bash
# 🎬 Restart instance
# ⚠️ Risk: 🟡 MEDIUM: Instance will be restarted, which may cause some services to be unavailable.
gcloud compute instances restart <instance> --zone <zone>
```
