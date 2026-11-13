# Ledger hand-off notes

One entry per build session (plan: `~/.claude/plans/users-acailic-downloads-xpn-ai-content-deep-wozniak.md`).

## Session L0: inventory and baseline (2026-11-12)

Read-only toward production: no n8n workflow changed or executed, nothing written to Supabase.

### Done
- Scrubbed baselines for Orchestrator, Content Provider and MEMES GENERATION in `baseline/`,
  with `scrub.py` (stdlib), its tests and a README on how L4 diffs a re-export.
- `INVENTORY.md`:
  - the paid-call tables: Content Provider and MEMES live, Moderation from a local export of
    2026-09-23;
  - item linkage, with the pairing of `Text creator model1` and `Create a row2`;
  - outcome mapping;
  - the Decline status string (`decline`);
  - the `created_at` timestamp on `xsolla_ai_posted_content_base`;
  - execution settings and the collector-vs-inline decision.
- `collector-n8n/prices.json`: BrightData (Web Scraper API, Web Unlocker), ffmpeg-api.com (null)
  and the koka.team parser (null), with sources, dates and open questions.
- `collector-n8n/fixtures/README.md`: why there are no fixtures yet, and how to fetch them.

### Not done
- **Baselines for Publisher, Moderation and Posting.** The connector cannot see them ("Available
  in MCP" is off). Publisher's paid nodes are therefore unverified, and `source_mismatch` and
  `no_channel` were not found anywhere that could be read.
- **Fixtures.** The connector has no way to read executions. Nothing was worked around.
- **No answer from an execution.** The "keeps `id`/`usage.cost`" column comes from config only.
- **Art/cosplay scope question:** answered on 2026-11-13, include both (see the addendum).

### Decisions
- **Collector (A), not inline nodes (B):**
  - No workflow overrides execution saving, and n8n's defaults save both successful and failed
    executions.
  - Retention was unknown on 2026-11-12. The 2026-11-13 addendum below gives it: 14 days, max
    250,000 executions.
  - Reason and conditions: `INVENTORY.md`, section 4.
- **Most model nodes need estimated cost.** Six of the nine model nodes read so far are LangChain
  OpenAI nodes with "Simplify Output" on, so their saved output has no `id` and no `usage`.
  Turning it off would break downstream expressions, so it is a pipeline change for later.
  - L4 estimates those calls (`cost_source = 'estimated'`).
  - L5 reconciles against OpenRouter.
- **ffmpeg-api.com stays unpriced (`null`).** It is a subscription in GB-seconds with no per-call
  price.

### Next
1. **You:**
   - ~~answer the Art/cosplay scope question~~ (done 2026-11-13: include both);
   - create a read-only n8n API key for `workflow.xsolla.com`. It unblocks the three missing
     baselines, the fixtures and L4.
2. **L4, first step with the key:**
   - export and scrub Publisher, Moderation (`yGyW6dWP3xfu446w`, capital W) and Posting;
   - complete the Publisher rows in `INVENTORY.md`;
   - check execution retention (oldest execution of each workflow ≥ 24 h) and that both success
     and error executions exist;
   - save fixtures.
3. **L1:**
   - add `commercial`, `invalid_source`, `model_error` and `scrape_failed` to the outcome values;
   - consider `media_process` and `moderator_translate` as purposes;
   - confirm the `created_at` default on `xsolla_ai_posted_content_base`.
4. **Pick one prices path:** the plan says `ledger/collector/`, this session used
   `ledger/collector-n8n/`.
5. **Recommend rotating** the Supabase service-role key hard-coded in two MEMES nodes, and the
   Telegram bot token hard-coded in five Moderation nodes.

### Checks run
- `python3 -m unittest discover -s ledger/baseline`: 9 tests pass.
- `python3 ledger/baseline/scrub.py --check ledger/baseline/*.json`: 0 leftover secret-looking
  strings in all three baselines.
- A grep of `ledger/` for Telegram bot tokens, `sk-` keys and literal Bearer tokens finds none.
  The only `eyJ` matches are the scrub regex, the made-up value in `test_scrub.py` and this line.
- Re-scrubbing each committed baseline gives identical bytes (idempotent), so a later diff only
  shows real changes.
- Header values in the six ffmpeg-api.com / BrightData nodes with `Authorization` headers, and in
  both MEMES Supabase-storage nodes, read back as `<redacted>`.
- Sources: the raw connector output for Content Provider is in this session's Claude tool-results
  folder, outside the repo. The Moderation export was read from `~/Downloads` and not copied.

### Addendum, 2026-11-13
- **Instance settings** came in from the planning session, read from `/rest/settings`. Successful
  and failed executions are saved with data, kept 14 days, max 250,000. Rule 1 holds at instance
  level, so the collector decision stands. Only Publisher's own settings are still unread.
- **Content Provider changed** to version `1d4f3543…`, with the user's approval. The Reddit
  snapshot check is now a loop of up to 15 checks, 90 s apart, and the `…Retry` nodes are
  disconnected.
  - Re-exported and re-scrubbed `baseline/ALobcKHwRGXxTkzG.json`. Its diff against the
    2026-11-12 version shows exactly that change and nothing else.
  - INVENTORY sections 1 and 4 are updated, including two collector notes: watermark on
    `stoppedAt` because of the `waiting` time, and up to 15 Get runs per execution.
- **Art generator (`PpzIpplWiA40Swzq`) and cosplay generator (`8zy4KFc7lc0j39sm`) are in the
  ledger.** That was the user's answer to the scope question.
  - INVENTORY now lists their paid nodes, from the node names and types the connector gave on
    2026-11-12: three LangChain model nodes, one embedding and the image calls in each. See
    sections 1, 2, 3 and 7.
  - Not done: their full exports and baselines. The connector lists both, but on 2026-11-13 every
    attempt to read them failed with a connector error (four tries). Next session: retry
    `get_workflow_details`, scrub to `baseline/`, then fill in providers, models, output settings
    and outcomes.
  - For L1: generated items have no lead behind them, and they bring new purposes
    (`art_prompt`, `art_text`, `art_style`; image calls use the existing `image_gen`).

- **Content Provider changed again**, to version `88c60c5d…`, at the user's request (reported
  by the planning session). The only change: the Reddit snapshot loop limit is now
  `$runIndex < 24`, so up to 25 checks in about 37 minutes.
  - Re-exported and re-scrubbed `baseline/ALobcKHwRGXxTkzG.json`. The diff against `1d4f3543…`
    is that one value plus `versionId` and `updatedAt`.
  - INVENTORY sections 1 and 4 now say 25 runs and about 37 minutes.
  - **Open for L5:** check that BrightData bills per record only. If it also bills per poll or
    snapshot download, the collector must price every run of `Get BrightData Reddit Snapshot`.
- **Art generator exported** (`40c79e15…`) into `baseline/PpzIpplWiA40Swzq.json`; INVENTORY
  sections 1, 2, 3 and 7 now use its real configuration.
  - It runs once a week (Wednesdays 00:00) and makes one image per run.
  - It writes a **story** (`xsolla_ai_content_provider`, status `new`) with no lead, not a post.
    Publisher then makes the posts. The L1 schema already allows this.
  - Its three LangChain nodes keep no `id`/`usage`, which makes nine of the fourteen model nodes
    read so far. `PIC Generating` keeps OpenRouter's `id` and cost.
- **Cosplay generator** is still not exported: three more connector errors on 2026-11-13.

## Session L1: schema and write API (2026-11-13)

Local only: nothing was applied to any real database. Tests run in a throwaway Docker container.

### Done
- `supabase/migrations/20261113000001_ledger_v001_tables.sql`:
  - schema `ledger` with `items`, `runs` and `steps` and their cost fields;
  - roles `ledger_writer` and `ledger_reader`;
  - RLS on with no policies, and no table grants for anyone.
- `supabase/migrations/20261113000002_ledger_v002_record_run.sql`:
  - `ledger.record_run(jsonb)`: idempotent, one transaction, refreshes the cost fields of the run
    and of every item tree it touched;
  - `ledger.recompute_costs()`, which returns what it changed;
  - the service-role-only wrapper `public.ledger_record_run(jsonb)`.
- `supabase/migrations/20261113000003_ledger_v003_views.sql`: 16 views for the read API, the Statistics tab, waste, outliers,
  fan-out and health. `ledger_reader` can read the views and nothing else.
- `WRITE_API.md`: the payload contract, the cost rules and what each view is for. L2, L3, L4 and L7
  start from it.
- `tests/`:
  - `run.sh` (Docker only) and four pgTAP files, 126 checks, covering everything in the plan's L1
    row: idempotent re-sends, NULL-not-0, `unpriced_calls`, the worked example to the cent, shares
    changing when a later Publisher run adds a post, `recompute_costs` matching the incrementally
    kept fields, and refusal for anon and authenticated;
  - `fixtures/worked_example.sql` holds the plan's example as payloads.

### Not done
- **Not applied anywhere real.** Applying to production is L5, and needs your approval at that step.
- **`ledger_n8n` login role not created.** It needs a password; create it at L4 or L5 and grant
  it `ledger_writer`.
- **Not tested against the real `xsolla_ai_posted_content_base`.** The live-status view assumes
  the columns `id`, `status`, `created_at` and `status_updated_at`, and the status values from the
  Orchestrator and the Moderation export. L5 checks them.

### Decisions
- **The ledger goes into the Supabase project that already holds the content and video pipeline
  tables** (user, 2026-11-13). `video-agent/.env` and the MEMES workflow's Supabase URLs name the
  same project, which is the one `supabase/migrations/` belongs to.
  - So the three migrations sit in `supabase/migrations/`, after the existing `game_assets` ones.
    They were first committed under `ledger/migrations/` on the wrong assumption that this folder
    was a video-only project.
  - Tests run with `ledger/tests/run.sh`, not `supabase test db`, because this Mac has no
    Supabase CLI. The script uses Docker and the `supabase/postgres:17.11.0.011` image, and
    applies every file in `supabase/migrations/` in order before the tests.
- **Steps are written once** (`ON CONFLICT DO NOTHING`, as the plan says). A re-send with changed
  flags or a late price is skipped, so collectors send a step only once its final state is known.
  If L3 or L4 need corrections, add an update path then.
- **"Known part" totals:**
  - A run whose calls are all unpriced has total 0 and `unpriced_calls` N.
  - Cost fields are NULL only when nothing was recorded: no run or step for the item, or a run
    sent with `cost_recorded: false` (legacy copy, L2).
  - `upstream_share_usd` is NULL for items without a parent, and when the parent's cost is
    unknown.
- **Parents:** story under lead, and post under story. Stories with no lead (the Art
  generator's) and videos have no parent (L0 addendum).
- **`purpose` is free text with a format check**, not a fixed list, so a new purpose never makes a
  payload fail. Names used so far are in INVENTORY.md and the plan.
- **Waste never double counts.** Each wasted cent sits under exactly one reason, tested:
  - money that bought nothing counts first (`failed_call`, `failed_run`);
  - dead ends then count their remaining ("clean") cost, including their share of the parent:
    `rejected:<outcome>`, `declined`, `post_error`.
- **Video approval** = run outcome `approved_final`, so the views don't depend on
  `video_agent_runs`. Publication per platform and cost per second of final video are not in the
  ledger: final duration isn't a column. L3 or L7 decides between adding it and reading
  `video_agent_runs`.
- **Health is two views:** `v_run_health_24h` (per workflow) and `v_provider_health_24h` (per
  provider).
- **Days are UTC.**

### Next
- **These can run in parallel now:**
  - **L2:** existing data.
  - **L3:** video collector.
  - **L7:** read API, against these views.
  - **L6:** Statistics mocks in these views' shapes.
- **L4** also needs the n8n API key.
- **L5** applies the three ledger migrations to that project, with your approval at that step:
  - Check the columns and status values of `xsolla_ai_posted_content_base` against
    `ledger.link_post_status()`.
  - The existing migrations were applied by hand, so the CLI's migration history may not list
    them. Apply the three ledger files by hand (SQL editor or `psql`), or repair the history before
    any `supabase db push`, so the push doesn't re-run `game_assets`.
- **Post statuses to check:**
  - the value for an expired ("overtime") post isn't known; until it is, it shows as stage
    `other`;
  - add it to `link_post_status()` once known.

### Checks run
- `ledger/tests/run.sh`:
  - all seven migrations in `supabase/migrations/` (four existing, three ledger) apply cleanly on a
    fresh database;
  - `01_security` 31, `02_record_run` 33, `03_worked_example` 36 and `04_views` 26 checks pass.
- A deliberately failing check made the runner print `FAIL` and exit 1, so a pass is real.
