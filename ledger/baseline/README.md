# Baseline exports of the n8n content-pipeline workflows

Scrubbed exports taken on 2026-11-12, before any ledger work touched n8n. L4 re-exports and
diffs against these to prove the production workflows were not changed.

| File | Workflow | versionId | updatedAt | Source |
|---|---|---|---|---|
| `hLCspmwIoGGalkGGDIIp1.json` | XSOLLA PIPELINE ORCHESTRATOR | `dba2e3b2-0990-4a6a-91d6-52d620424424` | 2026-09-15T13:07:15Z | n8n connector |
| `ALobcKHwRGXxTkzG.json` | XSOLLA CONTENT PROVIDER \| FOR UPDATES 3 | `ec44006e-bf04-4a3c-a77f-14fc8ebdae67` | 2026-09-22T07:59:51Z | n8n connector |
| `j0vjj8EVv1kKCtzx.json` | MEMES GENERATION | `b28d339e-f78e-489a-83d1-c73ccafd4466` | 2026-05-04T10:41:58Z | n8n connector |

Missing: Publisher `2SSIbhVPbKONRjcN`, Moderation `yGyW6dWP3xfu446w` and Posting
`iJNExgMktpMdK8bk`. The connector cannot see them because their "Available in MCP" setting is off.
Export them with the n8n API key (see `../INVENTORY.md`, section 5).

## What the scrub does

`scrub.py` (stdlib, Python 3.9+) keeps only the fields that describe behaviour. It:
- drops header and query values, keeping their names;
- reduces credentials to their names;
- redacts token-, key- and password-looking strings everywhere, Telegram bot tokens inside URLs
  included;
- sorts nodes and keys.

The same input always gives the same bytes. Exports from the connector carry no credential names,
because the connector strips them.

```bash
python3 ledger/baseline/scrub.py raw.json ledger/baseline/<id>.json   # scrub one export
python3 ledger/baseline/scrub.py --check ledger/baseline/*.json      # leftover secrets: paths only, never values
python3 -m unittest discover -s ledger/baseline                       # tests
```

## Proving "no production change" (L4)

```bash
# 1. re-export: GET https://workflow.xsolla.com/api/v1/workflows/<id> -> raw.json (keep it outside the repo)
python3 ledger/baseline/scrub.py raw.json /tmp/<id>.json
diff ledger/baseline/<id>.json /tmp/<id>.json   # must print nothing
```

An API export and a connector export differ in one way. The API export keeps credential names,
which the scrub reduces to `{"name": …}`, while the connector export has no `credentials` key at
all. If the diff shows only those lines, compare `versionId` and `updatedAt`: if they are unchanged,
the workflow is unchanged.
