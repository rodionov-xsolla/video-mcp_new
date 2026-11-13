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
  - For L1: generated posts have no lead or story behind them, and they bring new purposes
    (`art_prompt`, `art_text`, `art_style`, `image_generate`).
