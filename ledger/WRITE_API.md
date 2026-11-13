# Ledger write API and views

For the sessions that write to the ledger (L2 existing data, L3 video collector, L4 n8n collector)
and the one that reads it (L7 read API). Schema: `migrations/V001__tables.sql`. Functions:
`V002__record_run.sql`. Views: `V003__views.sql`.

## Calling it

| Caller | How | As |
|---|---|---|
| n8n collector (L4) | Postgres node: `select ledger.record_run($1::jsonb)` | a login role that is a member of `ledger_writer` (e.g. `ledger_n8n`; created at L4/L5, since it needs a password) |
| Python collector (L3) | `POST {SUPABASE_URL}/rest/v1/rpc/ledger_record_run` with body `{"payload": {…}}` | the service role |

One call is one transaction. If anything in the payload is invalid, nothing is written and the call
fails with SQLSTATE `22023` and a message that says what was wrong.

## Payload

```json
{
  "run": {
    "pipeline": "content",                  // content | video | influencer        (required)
    "workflow": "content_provider",         // lowercase, a-z 0-9 _                (required)
    "external_id": "184233",                // n8n execution id or video RUN_ID    (required)
    "status": "succeeded",                  // running | succeeded | failed | rejected | aborted (required)
    "outcome": "story_saved",               // free text: duplicate, disturbing, no_channel, approved_final, …
    "item": "lead",                         // ref of the item this run was for
    "workflow_version": "1d4f3543…",
    "started_at": "2026-11-13T10:00:00Z",
    "finished_at": "2026-11-13T10:02:00Z",
    "error_message": null,
    "source": "collector",                  // collector (default) | inline | backfill | legacy_copy
    "cost_recorded": true                   // false: this run's calls were not captured (legacy copy)
  },
  "items": [                                // parents before children
    {"ref": "lead", "kind": "lead", "source_table": "xsolla_ai_content_inbox", "source_id": "812",
     "game": "PALWORLD", "title": "…", "created_at": "2026-11-13T09:58:00Z"},
    {"ref": "story", "kind": "story", "parent": "lead",
     "source_table": "xsolla_ai_content_provider", "source_id": "455"}
  ],
  "steps": [
    {"idempotency_key": "n8n:184233:Clean_the_article:0:0",   // required, unique forever
     "item": "lead",                                           // default: the run's item
     "node": "Clean_the_article", "provider": "openrouter",    // provider required
     "model": "openai/gpt-4.1-mini", "purpose": "clean",       // purpose required, a-z 0-9 _
     "cost_usd": 0.0021, "cost_source": "estimated",
     "unit": "tokens", "units_in": 1800, "units_out": 600,
     "ok": true, "attempt": 1, "is_retry": false, "superseded": false,
     "error_message": null, "created_at": "2026-11-13T10:00:41Z"},
    {"idempotency_key": "n8n:184233:BrightData Reddit Scrape:0:0", "provider": "brightdata",
     "purpose": "scrape", "cost_source": "computed", "unit": "records", "units": 2, "unit_price_usd": 0.0015},
    {"idempotency_key": "n8n:184233:TG parser:0:0", "provider": "koka_team", "purpose": "scrape"}
  ]
}
```

Response: `{"run_id": 17, "steps_inserted": 3, "steps_skipped": 0, "items": {"lead": 41, "story": 42}}`.

### Rules

- **Items** are matched on `(source_table, source_id)`; `ref` names them only inside this payload.
  Listing an existing item fills its empty fields and updates the descriptive ones. Its `kind` and
  `parent` can't change: a different kind or parent is refused. Allowed parents: story under lead,
  post under story. Posts with no story (Art and cosplay generators) and videos have no parent.
- **Runs** are matched on `(workflow, external_id)`. A re-send updates status, outcome and finish
  time. A late `running` never moves a finished run back. A run can't be moved to another item.
- **Steps** are matched on `idempotency_key`. A key that exists is skipped, unchanged: steps are
  written once. Send a step when its final state is known: failed or not, superseded or not, price.
- **Cost:**
  - `cost_source` is required whenever `cost_usd` is given.
  - `computed` with no `cost_usd`: the function stores `units × unit_price_usd`.
  - No cost and no source: the step is stored as `unknown` with cost NULL. Never send 0 for an
    unknown cost.
  - `estimated` is for model calls whose node output keeps no `usage` (INVENTORY.md, section 1).

## What the function keeps up to date

In the same transaction, for the run and every tree of items the payload touched:

| Field | Value |
|---|---|
| `runs.total_cost_usd` | known cost of the run's steps; NULL only when `cost_recorded` is false and it has no steps |
| `runs.failed_attempts_cost_usd` | part of the total from steps with `ok = false` or `superseded = true` |
| `runs.unpriced_calls` | steps with cost NULL |
| `items.own_cost_usd` | known cost of steps with this `item_id`; NULL when no run or step was recorded for the item |
| `items.upstream_share_usd` | parent's total ÷ parent's number of children, rounded to 10 places; NULL without a parent or when the parent's cost is unknown |
| `items.total_cost_usd` | own + share |
| `items.unpriced_calls` | own unpriced calls + the parent's |

`ledger.recompute_costs()` rebuilds all of these from `steps` and returns
`{"runs_changed": n, "items_changed": m}`. On a consistent ledger both are 0, which makes it the
L5 consistency check.

## Views (all readable by `ledger_reader`)

Days are UTC dates. Spend columns hold the known part; `unpriced_calls` next to them counts what's
missing.

| View | Grain | For |
|---|---|---|
| `v_items`, `v_runs`, `v_steps` | one row per item, run, step | `/items`, `/items/:id`, `/runs`. `v_items` adds children, live post status and the last run |
| `v_post_live_status` | one row per post in `xsolla_ai_posted_content_base` | stage: waiting, approved, published, declined, error, other |
| `v_spend_day` | day × pipeline × workflow × node × provider × model × purpose × game × format | spend by purpose, top spenders, `/stats/purpose` |
| `v_cost_by_game_day`, `v_cost_by_format_day` | day × pipeline × game (or format) | `/stats/trend` |
| `v_content_stats_day` | day × game | Statistics tab, AI Content: posts generated, approved, rejected, published; leads rejected; spend; waste. Cost per published post = Σ spend ÷ Σ published over the period |
| `v_video_stats_day` | day × format × game | Statistics tab, Video: runs, approved videos (outcome `approved_final`), failed or aborted runs, spend, failed-attempt cost |
| `v_waste`, `v_waste_day` | one row per wasted amount; day × pipeline × game × reason | `/stats/waste`. Each cent is under one reason only: `failed_call`, `failed_run`, `rejected:<outcome>`, `declined`, `post_error` |
| `v_item_outliers` | posts and videos above the 95th percentile of their pipeline, kind and format | outliers, with the run to open |
| `v_fanout` | one row per story | what a story costs across its posts |
| `v_run_health_24h`, `v_provider_health_24h` | per workflow; per provider | `/health`, System Status |
| `v_item_clean_cost` | per item | helper for `v_waste` |

`v_post_live_status` reads `public.xsolla_ai_posted_content_base` when that table exists, and is
empty otherwise (fresh local database). If the table is created later, run
`select ledger.link_post_status();`.

## Testing

```bash
ledger/tests/run.sh        # needs Docker; starts a throwaway supabase/postgres, applies V001–V003, runs pgTAP
ledger/tests/run.sh 03     # one file
```

`tests/fixtures/worked_example.sql` holds the plan's worked example as payloads, a good starting
point for collector fixtures.
