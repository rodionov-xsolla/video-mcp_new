# Execution fixtures for the n8n collector

Empty on purpose. The n8n connector used in L0 cannot read executions, so no fixtures exist yet.

Needed: one success, one rejected or stopped, and one failed execution for each of Content
Provider, Publisher, MEMES GENERATION and Moderation. Fetch them with an n8n API key:

```bash
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://workflow.xsolla.com/api/v1/executions?workflowId=<id>&status=success&includeData=true&limit=1" > raw.json
python3 ../../baseline/scrub.py raw.json <workflow>-success-<executionId>.json
```

Before committing, also blank personal data, which `scrub.py` does not touch: post text, Telegram
user and chat ids, moderator names.

Name files `<workflow>-<success|rejected|failed>-<executionId>.json`. Details are in
`../../INVENTORY.md`, section 5.
