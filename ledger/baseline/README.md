# Baseline exports of the n8n content-pipeline workflows

Scrubbed exports, taken before any ledger work touched n8n. L4 re-exports and diffs against these
to prove the production workflows were not changed by the ledger.

| File | Workflow | versionId | updatedAt | Exported | Source |
|---|---|---|---|---|---|
| `hLCspmwIoGGalkGGDIIp1.json` | XSOLLA PIPELINE ORCHESTRATOR | `dba2e3b2-0990-4a6a-91d6-52d620424424` | 2026-09-15T13:07:15Z | 2026-11-12 | n8n connector |
| `ALobcKHwRGXxTkzG.json` | XSOLLA CONTENT PROVIDER \| FOR UPDATES 3 | `88c60c5d-1e46-4fa7-a4e6-50ccaa84c334` | 2026-11-13T14:25:55Z | 2026-11-13 | n8n connector |
| `PpzIpplWiA40Swzq.json` | XSOLLA Art generator pipeline | `40c79e15-4931-4543-8d95-45e25fe18e50` | 2026-09-15T13:07:21Z | 2026-11-13 | n8n connector |
| `j0vjj8EVv1kKCtzx.json` | MEMES GENERATION | `b28d339e-f78e-489a-83d1-c73ccafd4466` | 2026-05-04T10:41:58Z | 2026-11-12 | n8n connector |

Content Provider was changed on purpose twice on 2026-11-13, at the user's request. Neither change
is related to the ledger, and the file was re-exported after each:
- `ec44006e…` → `1d4f3543…`: the Reddit BrightData snapshot check became a loop, 90 s apart.
  The previous file is in commit `819de5c`.
- `1d4f3543…` → `88c60c5d…`: the loop limit went from `$runIndex < 14` to `< 24`, so up to 25
  checks. The previous file is in commit `2c224ab`.

Each diff shows exactly the described change and nothing else, which also shows the recipe below
works. If a workflow changes again for reasons other than the ledger, re-export it before L4 uses
it as the "unchanged" reference.

Missing: Publisher `2SSIbhVPbKONRjcN`, Moderation `yGyW6dWP3xfu446w` and Posting
`iJNExgMktpMdK8bk`. The connector cannot see them because their "Available in MCP" setting is off.
Export them with the n8n API key (see `../INVENTORY.md`, section 5).

Also missing: cosplay generator `8zy4KFc7lc0j39sm`, which joined the ledger on 2026-11-13 with the
Art generator. The connector can see it, but it returned errors on every read that day. Export it
with the connector or the API key.

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
