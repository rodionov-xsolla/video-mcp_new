# XPN AI Content — cost ledger build plan

> **Status of this file.** This is the build plan as approved on 2026-11-12. Progress, and every
> decision made since, are in [`HANDOFF.md`](HANDOFF.md), one entry per build session. Since
> approval: L0 and L1 are done; L0 confirmed the collector approach; the n8n price list lives in
> `ledger/collector-n8n/prices.json`; and the Content Provider's Reddit snapshot check was changed
> on 2026-11-13 (HANDOFF.md, L0 addendum). The two pages linked below are private Claude
> artifacts; ask Aleksandar Ilić for access.

Visual version, with diagrams, every cost field explained, the worked example and example charts:
https://claude.ai/artifact/A4tT6ihGhSePdW9aFfeZ5e

Architecture (write API, collectors, read API, full table schemas, tools):
https://claude.ai/artifact/B3JT9czwHBz5VrpFfcb1um

## Build now vs. after the AI Engineer arrives

The ledger is built from a stable core (the three tables, `record_run()` and the views) and small
adapters (the collectors). Moving video generation to a server, or replacing n8n, changes only
an adapter.

| When | What | Why |
|---|---|---|
| **Now** | L0 inventory, L1 schema and write API, L2 existing data, L4 n8n collector | No pipeline changes. Gives the AI Engineer real cost numbers on day one |
| **Now, kept thin** | L3 video collector, laptop runs only | Small and cheap to rewrite. Cost per video is itself an input to the server decision |
| **After the AI Engineer arrives** | Where the read API is hosted (L7 deploy), which repo the code lives in (D1), how video moves to a server, per-attempt video writes, any change inside the pipelines | These are architecture choices the AI Engineer may change |

## Architecture in one paragraph

- **Writes:** one PL/pgSQL function inside the database, `ledger.record_run(payload jsonb)`, is
  the only way in. It is idempotent, runs in one transaction, and refers to items by their
  pipeline ids (`source_table` + `source_id`).
- **Collectors** are separate programs that live next to their data, not part of any API:
  - an n8n workflow (Schedule → n8n "Get executions" → Code node with the repo's `extract.js` →
    Postgres node calling `record_run`, logged in as `ledger_n8n`, a member of `ledger_writer`);
  - a stdlib Python tool inside the video agent (`finish` at the end of a run, `sweep` on a
    schedule), calling `record_run` over Supabase RPC. It runs wherever the agent runs, so moving
    the agent to a server changes nothing in it.
- **Reads:** the panel's read API is a small TypeScript service (Node 22, Hono, postgres.js,
  zod). It reads only the views, as `ledger_reader`, and serves the mini-app through
  `/api/mini-app-proxy/xpn-ai-content/…`. It runs on Cloud Run later and against a local Supabase
  now.
- **Schema and tests:** migrations are SQL in `supabase/migrations/` (Supabase CLI, which the repo
  already uses), tested with pgTAP (`supabase test db`).

## Context

Most of the XPN AI Content work waits for the incoming AI Engineer (BDXPN-2290), who may change the
pipeline design. Two things can go ahead now: the frontend, whose UI already exists on
`mini-apps/xpn-ai-content-v0.1.0`, and the **cost ledger**. This plan covers the ledger.

The ledger records every pipeline run and every paid call with its cost, in Supabase/Postgres
tables `items`, `runs` and `steps` (build guide S2/S3). Today nothing records cost:
- The content pipeline (n8n) stores no cost per call or per post.
- The video agent has a `video_agent_runs.total_cost_usd` column that nothing writes. Its cost report
  is typed into chat by hand, and failed runs never reach the database.

The ledger gives the AI Engineer real numbers before any redesign, as *Possible Improvements* asks:
cost per post, story and video; spend on rejected leads; and failure and retry cost.

Design rule, because the pipelines may change: **the ledger must not depend on how the pipelines
are built, and it must not change them.** Phase 1's rule applies: only add ledger writes, and a
failed ledger write never stops a post.

## Facts the design rests on

**Content pipeline (n8n, Supabase)**
- Six workflows: Orchestrator, Content Provider `ALobcKHwRGXxTkzG`, Publisher `2SSIbhVPbKONRjcN`,
  Moderation `yGyW6dWP3xfu446w`, Posting `iJNExgMktpMdK8bk`, MEMES GENERATION `j0vjj8EVv1kKCtzx`.
- **Every model call goes through OpenRouter**, including OpenAI models; there is no OpenAI
  account. OpenRouter reports the actual cost of each call, so model cost can be taken as
  reported, not computed from a price list.
- Paid calls in Content Provider, checked through the n8n connector on 2026-11-12:
  - Model nodes, `@n8n/n8n-nodes-langchain.openAi` pointed at OpenRouter: `Clean_the_article`,
    `Analyze image`, `Analyze Image` (in the gallery loop) and `Get_community`.
  - `Generate Embedding` (HTTP Request).
  - BrightData: `BrightData Scrape`, `Scrape1`, `Scrape2`, `Reddit Scrape` and the snapshot polls.
  - The ffmpeg service: `Merge content`, `Probe Video`, `Compress Video` and the upload nodes.
- Paid calls in the other workflows, from the docs (L0 confirms the node names):
  - Publisher: `Text creator model` once per channel, and the image-generation request.
  - MEMES GENERATION: an image model once per language.
  - Moderation: "AI Editing".
- The same instance has other active content workflows, "XSOLLA Art generator pipeline" and
  "XSOLLA cosplay generator pipeline", which also make model calls. L0 checks with you whether they
  belong in the ledger.
- Units of content:
  - one inbox lead (`xsolla_ai_content_inbox`) becomes 0–2 stories (`xsolla_ai_content_provider`;
    a mixed image-and-video item splits in two);
  - one story becomes one post per channel (`xsolla_ai_posted_content_base`).
- Leads rejected as disturbing, source mismatch, duplicate or forbidden tag have already paid for
  model calls but leave no story row.
- No local export of the workflows exists, but **the n8n connector in this app can read the
  instance**, so L0 can run from a session that has it. Still unknown: whether each model node's
  output keeps OpenRouter's generation `id` and `usage`, which depends on the node's output
  settings.

**Video agent (`video-mcp_new`, remote `github.com:rodionov-xsolla/video-mcp_new`)**
- One `RUN_ID` per video, with `OUTPUT_DIR=output/YYYY-MM-DD/{GAME}/{format}/{RUN_ID}/`. The
  `RUN_ID` never reaches Supabase; the database key is `output_video_url`, which exists only after
  approval.
- `tools/kling_runner.py` writes `build/video/<job_id>/state.json` (schema v3). It holds `route`
  (which stands in for the model), `attempts[]` with `request_id`, a phase that can be FAILED,
  UNKNOWN or PAID_RETRY_REQUIRED, and `validation.duration`, the billed length from ffprobe. Audio
  on/off is in `request.json`. `tools/fal_runner.py` writes `build/fal/<job_id>/` for NB2 images.
- Neither runner keeps fal's billing data, so cost must be computed as duration or images × price.
- Prices for every fal model are in `rules/main/budgets.md`, `rules/roles/manager.md` and
  `providers.json` "pricing". Of the three copies, only `providers.json` is machine-readable.
- Calls that leave no state file: TTS, music and SFX (direct curl in `rules/roles/sound.md`),
  possibly Kling Avatar, and the Claude sub-agents' own usage.
- `queue/log-video.sh` upserts `video_agent_runs` over PostgREST, using `SUPABASE_URL` and
  `SUPABASE_SERVICE_ROLE_KEY` from `video-agent/.env`, and only after approval.
- Existing tables have RLS with allow-all policies.
- Repo conventions: bash and stdlib Python 3.9, `unittest` in `tools/tests/`, no CI. SQL lives in
  `supabase/migrations/` and `queue/setup.sql`, both applied by hand.
- **The video agent runs on one person's laptop today and will almost certainly move to a
  server.** BDXPN-2291 puts runs behind the control panel, and the `video_tasks` queue table
  already exists. Nothing on the video side of the ledger may depend on the laptop.

## Design

### Where it lives

A self-contained `ledger/` folder in `video-mcp_new` holds the migrations, write API, collectors,
tests and docs. This repo already holds the video Supabase schema, and the video collector has to
live there anyway. A self-contained folder moves easily if the team's backend-location decision (D1,
appendix) picks another repo. **Flag for D1:** the repo is under a personal GitHub account
(`rodionov-xsolla`), not the `xsolla` org.

### Schema (Postgres schema `ledger` in the pipeline's Supabase project)

There are exactly three tables, as in the build guide. Cost is stored on `items` and `runs`, and
`steps` keeps the per-call detail behind it.

**What the item kinds mean**

| Kind | One row per | Comes from | Example |
|---|---|---|---|
| lead | link that arrived from an RSS feed | `xsolla_ai_content_inbox` | a Reddit post about PALWORLD |
| story | cleaned, accepted piece of content made from a lead. Usually one per lead; two when a post had both images and video | `xsolla_ai_content_provider` | the cleaned PALWORLD article with its picture |
| post | story written for one channel | `xsolla_ai_posted_content_base` | the Russian Telegram version of that story |
| video | video produced by the video agent | `video_agent_runs` / `RUN_ID` | a 30-second PALWORLD short |

- **`items`**: one row per lead, story, post or video. It answers **"what did this post or video
  cost, all in?"**
  - `kind` and `pipeline` (content, video or influencer); `parent_id` (post → story → lead);
    `source_table` and `source_id` (unique together); `game`, `format`, `channel_id`,
    `channel_type`, `language`, `title`, `created_at`.
  - Cost fields: see "Cost fields explained" below.
- **`runs`**: one row per execution of a workflow, or per video run. It answers **"what did this one
  execution cost?"**
  - `pipeline` (content, video or influencer, the same as on `items`), so each panel section can
    filter its own runs.
  - `workflow` (content_provider, publisher, memes, moderation_ai_edit, video_agent) and
    `external_id` (the n8n execution id or `RUN_ID`), unique together.
  - `workflow_version`, `item_id`, and `status`: running, succeeded, failed, rejected or aborted.
  - `outcome`: duplicate, disturbing, source_mismatch, forbidden_tag, no_channel, approved_final, …
  - `started_at`, `finished_at`, `error_message`, and `source`: collector, inline, backfill or
    legacy_copy.
  - Cost fields: see below.
- **`steps`**: one row per paid call, such as one model request, one scrape or one video clip.
  It is the evidence behind every cost field.
  - Each step names its run (`run_id`) and the item it served (`item_id`).
  - `idempotency_key` (unique) stops a re-send from counting twice, e.g.
    `n8n:<exec>:<node>:<runIndex>:<itemIndex>` or `video:<job_id>:<attempt>`.
  - `node`, `provider` (openrouter, brightdata, ffmpeg_service, fal, …) and `model`.
  - `purpose`, the same categories across both pipelines: scrape, clean, community, embed, vision,
    media_merge, image_gen, localize, meme_translate, ai_edit, image, clip, lipsync, tts, music.
  - `ok` (true or false), `error_message`, `attempt`, `is_retry`, `superseded`, `created_at`.
  - Cost fields: see below.

### Cost fields explained

**Rule for every cost field:** NULL means "we don't know", never zero. 0 appears only for a call
known to be free, such as a still shot. When some calls behind a total are priced and some aren't,
the total holds the known part, and `unpriced_calls` says how many are missing. The UI then shows
"≥ $0.12 (1 call not priced)".

| Field | On | What it means in plain words | How it's filled |
|---|---|---|---|
| `cost_usd` | steps | What this one call cost | Text and image models: OpenRouter's reported cost. BrightData, ffmpeg and fal: `units × unit_price_usd` |
| `cost_source` | steps | How we know the cost: `reported` (OpenRouter told us), `computed` (units × our price), `estimated` (approximation), `unknown` (cost is NULL) | Set by the collector |
| `unit` | steps | What the call is billed by: tokens, images, seconds, records, calls | From the node map or the runner |
| `units_in`, `units_out` | steps | For text models, the input and output tokens. Information only, since OpenRouter's reported cost already includes them | From the response's usage |
| `units` | steps | Billed quantity for non-token calls: 5 (seconds of clip), 1 (image), 120 (scraped records) | From the response or `state.json` |
| `unit_price_usd` | steps | The price per unit used for a computed cost, kept on the row so later price changes never rewrite old costs. Empty for reported costs | From `providers.json` or `prices.json` |
| `total_cost_usd` | runs | Everything spent during this one execution | Sum of the run's steps |
| `failed_attempts_cost_usd` | runs | The part of the total spent on calls that failed or were redone: money that bought nothing. Already included in the total | Sum of steps that failed, or that a later retry superseded |
| `unpriced_calls` | runs, items | How many paid calls behind the total have no known price. If above 0, the total is a lower bound | Count of steps with NULL cost |
| `own_cost_usd` | items | Calls made specifically for this item. For a post: writing it for its channel, translating its meme, AI edits. For a lead: the scrape and checks made before a story existed. For a video: every call in its run | Sum of steps whose `item_id` is this item |
| `upstream_share_usd` | items (story, post) | This item's equal share of what was spent on its parent before it existed. A post gets its story's total ÷ the number of posts made from that story; a story gets its lead's own cost ÷ the number of stories made from that lead | Recomputed when the parent's cost or its number of children changes |
| `total_cost_usd` | items | **What this item cost, all in:** own + upstream share. For a post, this is the cost per post. For a video, the cost per video | own + upstream share |

**Worked example (illustrative numbers):**

- **One lead, four posts.** A PALWORLD Reddit link (lead #812) goes through one Content Provider
  run and one Publisher run.

  | Item | own | upstream share | total |
  |---|---|---|---|
  | Lead #812: scrape 0.0030 + clean 0.0021 + community 0.0004 + embedding 0.0001 + image analysis 0.0034 | 0.0090 | — | 0.0090 |
  | Story #455: image generation 0.0400 | 0.0400 | 0.0090 ÷ 1 story = 0.0090 | 0.0490 |
  | Post: Telegram RU, localization 0.0012 | 0.0012 | 0.0490 ÷ 4 posts = 0.01225 | **0.01345** |
  | Posts: Telegram EN 0.0011, Discord 0.0010, X 0.0009 | … | 0.01225 each | 0.01335 / 0.01325 / 0.01315 |

  - Run totals: Content Provider 0.0090 and Publisher 0.0442, together 0.0532.
  - The four posts' totals add up to 0.0532 too. The split moves cost down to the posts and never
    creates or loses money.
- **A rejected lead.** Lead #813 is a duplicate: scrape 0.0030 + clean 0.0021 + embedding 0.0001
  = 0.0052. It has no story, so the cost stays on the lead and shows up as waste ("rejected:
  duplicate").
- **A video.** Six images at 0.08 = 0.48, plus five 5-second clips at 0.084/s = 2.10, plus one clip
  that failed after being billed and was redone, 0.42.
  - Run `total_cost_usd` = 3.00 and `failed_attempts_cost_usd` = 0.42.
  - The TTS call has no record, so `unpriced_calls` = 1, and the video shows "≥ $3.00 (1 call not
    priced)".

**How to get totals without double counting:**
- Total spend is the sum of `runs.total_cost_usd` (or of `steps.cost_usd`).
- Never add up `items.total_cost_usd` across kinds: a story's total already sits inside its posts'
  totals.
- Per-post and per-video figures come straight from `items` where kind = post or video.
- **No prices table.** Prices live in the collectors' config, versioned in git:
  - the video collector reads `providers.json` "pricing";
  - the n8n collector needs prices only for non-model calls, because OpenRouter reports model
    cost. These live in `ledger/collector-n8n/prices.json`: BrightData per record and the ffmpeg
    service, if it charges per call.

  The n8n collector keeps its watermark in the workflow's static data, so no state table is
  needed either.
- **Security:** RLS on with no anon policies; this is a deliberate break from the existing allow-all
  tables. Writes go only through the write function under the service role or a dedicated writer
  role. A read-only `ledger_reader` role gets SELECT on the views, for the panel's backend later.

### Write API

`ledger.record_run(payload jsonb)` takes a run, its item references (creating or linking items) and
a steps array:
- The run is upserted on `(workflow, external_id)`, which updates status and finish time.
- Steps are inserted with `ON CONFLICT (idempotency_key) DO NOTHING`, so re-sending is safe.
- In the same transaction it refreshes the cost fields it touched:
  - the run's `total_cost_usd`, `failed_attempts_cost_usd` and `unpriced_calls`;
  - each affected item's `own_cost_usd`;
  - when a lead's or story's cost or number of children changes, the `upstream_share_usd` and
    `total_cost_usd` of all its children. A story's posts can arrive in a later Publisher run,
    which changes every post's share.

  A `ledger.recompute_costs()` function rebuilds every cost field from `steps`. It runs after a
  backfill and as a consistency check.

A thin `public.ledger_record_run(jsonb)` wrapper, granted to the service role only, makes the
function callable over PostgREST RPC by the Python collector without exposing the `ledger` schema.
n8n calls the function itself through its existing Postgres credential.

### Cost per run, per post, per video: where to read each

- **Per run:** `runs.total_cost_usd` and `failed_attempts_cost_usd`. The breakdown by purpose
  inside a run comes from its `steps`.
- **Per post:** `items.total_cost_usd` where kind = post. A post's live outcome (published,
  waiting, declined, overtime) comes from joining `xsolla_ai_posted_content_base` in the same
  database. Status is never copied, so it can't go stale.
- **Per video:** `items.total_cost_usd` where kind = video. The breakdown by purpose and the cost
  per second of the final video come from its `steps`; approval comes from `video_agent_runs`.

### Insight queries (savings and problem spots)

These are plain SQL views over the three tables, not extra tables. L5 uses them for the first
findings:

- **Cost per published output:** all spend ÷ published posts (or approved videos), by game,
  format and channel. The true unit cost, waste included.
- **Waste:**
  - spend on posts that were declined or expired (overtime);
  - spend on leads rejected before any post, by reason (duplicate, disturbing, source mismatch,
    forbidden tag) and by source feed;
  - spend on failed and retried calls (`PAID_RETRY_REQUIRED` and n8n failures).
- **Top spenders:** cost by node, model and purpose, which shows which call to cheapen first.
- **Outliers:** posts and videos above the 95th-percentile cost for their format, with a link to the
  run.
- **Fan-out cost:** what one story costs as it fans out to N channels and M languages. A
  twelve-channel story is twelve localization calls.
- **Trends:** daily cost by game and format (`v_cost_by_game_day`, `v_cost_by_format_day`).
- **Health:** `v_run_health_24h` per provider and workflow (last success, error count, last error),
  which also feeds System Status.

### Statistics per panel section

The panel's Statistics tab shows only the pipeline of the sidebar section it sits in. The columns
differ per pipeline, so each has its own view, filtered on `pipeline`. All figures are per game,
for the selected period (7 / 30 / 365 days / all time), with a Total row.

| Section | Statistics columns | Charts |
|---|---|---|
| **XPN AI Content** (n8n) | Members / growth*; posts generated, approved, rejected, published; spend; cost per published post; waste | Spend by purpose; waste by reason; cost per published post over time, by game |
| **XPN Video Generation** | Runs; approved videos; published on YouTube / TikTok / Instagram; failed or aborted runs; spend; cost per approved video; failed-attempt cost; cost per second of final video | Spend by purpose (images, clips, lip-sync, TTS, music); cost per video by purpose; cost per approved video over time, by format; waste (failed attempts, aborted runs, superseded takes) |
| **XPN AI Influencer** | "In progress": nothing is built yet (BDXPN-2284). The ledger already accepts `pipeline = 'influencer'`, so its statistics are defined once the design exists | — |

\* Members / growth comes from a small channel member-count job, not from the ledger. YouTube
subscriber counts for the video section need a YouTube login with read scopes (BDXPN-2288).

### How runs get written: collectors, not changes to the pipelines

- **Content pipeline.** A new n8n workflow, **LEDGER COLLECTOR**, runs on a cron every 15 minutes
  on the same instance, so no cloud environment is needed.
  - It reads finished executions of the six workflows from the n8n API, with their data, since its
    watermark.
  - A pure JS extractor uses a versioned node map (node name → provider, model, how to read usage,
    how to link the item) to turn each execution into a `record_run` payload.
  - Nodes that look paid but aren't in the map are recorded as `unmapped`, so a redesign by the AI
    Engineer shows up instead of silently dropping cost.
  - **Model calls (all OpenRouter):** the cost comes from the response's `usage.cost`, or, if only
    the generation `id` survived, from OpenRouter's generation endpoint (`provider_reported`).
    `steps.model` records the model and upstream provider OpenRouter actually used, so the same
    model served at different prices shows up.
  - If a node's output drops both `id` and `usage`, L0 lists it. That node then needs its output
    setting changed (a small node change, made only with your approval), or its cost is
    estimated from text length (`estimated`).
  - **Non-model calls** (BrightData, the ffmpeg service) are priced from
    `ledger/collector-n8n/prices.json` (`computed`), or left NULL when there is no per-call price.
  - Why a collector rather than ledger nodes inside the workflows, and when to fall back: see
    "Collector vs inline writes (n8n)" below.
- **Video agent.** A new `video-agent/tools/ledger_collect.py` (stdlib Python). It is built to run
  wherever the video agent runs: a laptop today, a server once the agent moves (BDXPN-2291).
  - Two commands:
    - `finish <OUTPUT_DIR>`, called when a run ends (approved, failed or aborted);
    - `sweep <root> --older-than 2h`, run on a schedule. It records runs that never called
      `finish` (crashes, aborts), marks runs that stalled as `aborted` with their cost so far, and
      backfills past runs still on disk.
  - It reads the run's `build/video/*/state.json` and `build/fal/*/` files, and prices each billed
    attempt from `route`, `validation.duration` or the image count, audio from `request.json`, and
    the `providers.json` pricing.
  - Both commands send the same idempotent payload, keyed by `RUN_ID`, so a run is counted once
    however often it's sent. The item is linked to `video_agent_runs` through `output_video_url`
    once that exists.
  - Its settings come from environment variables: `.env` on the laptop, the secret store on a
    server.

  | | Today, on the laptop | Later, on a server |
  |---|---|---|
  | `finish` | The manager calls it at the end of a run, next to the existing `log-video.sh` call | The worker calls it in its cleanup step, so it runs even when the job fails |
  | `sweep` | By hand, or as a daily scheduled task | A scheduled job on the server |
  | Run id | `RUN_ID` | The queue's `video_tasks.id`, so panel requests, queue rows and ledger runs share one id |
  | Requirement on the host | — | Keep each run's `build/` state files until `sweep` has read them, or upload them with the outputs |

  - The docs expect a **cloud job**: build guide Phase 3 ("Video agent in the cloud,
    BDXPN-2291"), and *Possible Improvements* (Agent SDK or non-interactive Claude Code "inside a
    cloud job"). A job's disk is wiped when it ends. There, `finish` in the job's cleanup step is
    the main path, and the state files must be uploaded with the outputs for `sweep` to work.
  - Later option, once a server worker exists: the runners report each billed attempt as it
    happens, which gives live cost during a run.
  - TTS, music and SFX calls and Claude usage stay "not recorded" for now. A follow-up is a small
    `record-call` command for the curl calls in `sound.md`.

### Collector vs inline writes (n8n)

There are two ways to get cost out of the four n8n workflows that make paid calls (Content
Provider, Publisher, MEMES GENERATION, and Moderation's AI edit).

**A. Collector (pull), recommended.**
- n8n already saves every execution, with each node's output. That output includes OpenRouter's
  cost for model calls.
- A new, separate workflow, LEDGER COLLECTOR, runs every 15 minutes:
  1. It asks the n8n API for executions of the four workflows that finished since its last
     watermark, with their data, page by page.
  2. A Code node walks each execution's node outputs with a versioned node map:
     - which nodes are paid, and where their cost sits;
     - which node holds the item id: `Extract Inbox Item ID` → lead, `Save the Post` → story,
       `Create a row` → post;
     - which stop node means which outcome: `Duplicated Post` → duplicate, `Disturbing Post` →
       disturbing, and so on.
  3. It sends one `record_run()` payload per execution and moves the watermark forward.
- Manual and test executions are skipped.
- A paid-looking node missing from the map is recorded as `unmapped`. A redesign then raises an
  alarm instead of silently dropping cost.

**B. Inline (push).**
- Ledger nodes are added inside the production workflows. Before every exit of each workflow (the
  success end and every stop node, such as Disturbing, Commercial, Duplicated, Forbidden and the
  error stops), a Code node gathers usage from the earlier nodes that ran.
- It then calls a shared "LEDGER WRITE" sub-workflow, without waiting, with continue-on-error.
  Content Provider alone has around eight exits, so that is roughly 10–15 added nodes across the
  four workflows.
- A node that crashes ends the execution before any ledger node runs, so that execution's cost is
  lost. Catching it needs an Error Workflow, which only gets the execution id and would itself
  have to read the execution's data, which is option A anyway.

| | A. Collector | B. Inline |
|---|---|---|
| Changes to production workflows | None | A ledger node before every exit (~10–15 nodes in 4 workflows) |
| Failed executions | Captured, with the calls made before the failure | Lost when a node crashes, unless every failure path is wired |
| Rejected leads | Captured; the stop node's name gives the reason | Captured only where a ledger node sits before that stop |
| History | Backfills executions n8n still keeps | Starts on the day it's added |
| Delay | Up to 15 minutes (fine for a dashboard) | Immediate |
| Depends on | n8n keeping execution data for success and error for at least a day; an n8n API key | Nothing extra |
| When the AI Engineer changes a workflow | Update one node map; renamed nodes raise an "unmapped" alarm | Re-add and re-test ledger nodes in each changed workflow |
| Risk to posting | None: it runs beside the pipeline | Small but real: each edit is a production deploy |
| Effort | 1 new workflow, plus an extractor tested on fixtures | Edits in 4 workflows, plus a sub-workflow |

**Collector risks and their handling:**
- Execution data can be pruned before it's read. The watermark plus a 15-minute cadence keep the
  window small, and the "Save execution data" settings are checked at L0.
- Execution payloads are large. The collector reads them in pages, with a per-tick limit.
- Per-post cost depends on matching each `Text creator model` call to its `Create a row` by
  loop index. L0 checks this on real executions.

**Decision rule, applied at L0:**
1. If the four workflows save successful and failed production executions, and the instance keeps
   them for at least 24 hours, use A.
2. If successful executions are not saved, turn saving on for just those four workflows. That is a
   workflow setting, not a node change, and needs your approval. Then use A.
3. Use B only if that setting can't be changed.

### Existing data

- `video_agent_runs` rows are copied into items (video) and runs (`legacy_copy`), with cost NULL
  unless `total_cost_usd` is set. The copied run count must equal the source table's row count.
- Existing stories and posts get items with no runs, which shows as "not recorded".

## Build sessions

Each session ends with a note in `ledger/HANDOFF.md` using the build guide's template (Done, Not
done, Decisions, Next, Checks run).

| ID | Session | Where | Needs | Done when |
|---|---|---|---|---|
| L0 | **Inventory and baseline (read-only, through the n8n connector).** Export the six workflows to `ledger/baseline/` **with credentials and header values removed**: two MEMES nodes carry a hard-coded Supabase key (0.3), so never echo node headers into chat or commit them. For every paid node, record workflow, node, type, provider, model, unit, whether the output keeps OpenRouter's `id` and `usage.cost`, and the field that links it to an item. Ask whether the Art generator and cosplay workflows are in scope. Record n8n's execution save and prune settings. Save 2–3 scrubbed executions per workflow as fixtures. Check Supabase for the status value a Decline writes and for creation timestamps. Build `ledger/collector-n8n/prices.json` from the providers' price lists, with sources and dates. Decide collector vs inline | n8n (UI or API, with your access) + Supabase read + `video-mcp_new` | n8n read access | `ledger/INVENTORY.md` committed; fixtures committed; collector-or-inline decided and noted |
| L1 | **Schema and write API.** Migrations V001 (the three tables with their cost fields, RLS, roles), V002 (`record_run` with its cost-field refresh, `recompute_costs`, the RPC wrapper), V003 (the insight views). SQL tests against a local Supabase (`supabase start`; the repo has `supabase/config.toml`) for: idempotent re-sends; NULL-not-0 cost fields; `unpriced_calls` counts; the worked example above reproduced exactly (the four posts' totals add up to the runs' total, and the shares change when a later Publisher run adds a post); `recompute_costs` reproducing the incrementally kept fields; refusal for anon | `video-mcp_new/ledger/` | L0 | Migrations apply cleanly on a fresh local DB; tests pass |
| L2 | **Existing data.** Copy script for `video_agent_runs`, plus items for existing stories and posts | `ledger/` | L1 | On a local copy, copied runs = source rows; no copied cost is 0 |
| L3 | **Video collector.** `tools/ledger_collect.py` with `finish` and `sweep`. Settings come from environment variables only, with no laptop paths. `unittest` tests on fixture run folders (success, FAILED, PAID_RETRY_REQUIRED, audio on/off, crashed mid-run). Add the manager's `finish` call next to `log-video.sh`. Write a short note for BDXPN-2291 on what a server worker must do: call `finish` in cleanup, schedule `sweep`, keep state files until swept, use `video_tasks.id` as `RUN_ID` | `video-mcp_new` | L1 | Fixture runs price correctly; one real run is recorded by `finish`; `sweep` records a crashed fixture run as aborted and counts nothing twice |
| L4 | **Content collector.** The LEDGER COLLECTOR workflow (or inline sub-workflow, per L0), the extractor as a pure function tested with node against L0 fixtures, the watermark, the unmapped-node alarm, and a backfill of retained executions | n8n + `ledger/collector/` | L1; n8n API key stored as an n8n credential | Fixture executions produce the expected payloads; a PALWORLD run of each workflow produces runs and steps with cost; production workflows unchanged (diff against `baseline/`) |
| L5 | **Go live and reconcile.** Apply the migrations to the production Supabase (additive `ledger` schema, **with your approval at that step**), turn on both collectors, run a week, compare totals per provider with OpenRouter's activity and key usage, and with the fal and BrightData billing dashboards, and write up the first findings: unit cost per published post and video, waste by reason, top spenders, outliers and fan-out cost, with the three biggest savings candidates | Supabase + n8n | L2–L4 | Totals within ±10 % of billing, or the gaps explained; findings note for the AI Engineer |
| L7 | **Panel read API, local.** TypeScript service (Hono, postgres.js, zod) with `/stats`, `/stats/purpose`, `/stats/waste`, `/stats/trend`, `/items`, `/items/:id`, `/runs` and `/health`, reading views as `ledger_reader`. Vitest against a local Supabase seeded with example data, plus a Dockerfile. The Vite dev proxy lets the mini-app call it locally. Deploying and the Service Desk proxy ticket wait for the cloud environment | `ledger/api/` | L1 views | Every endpoint returns the documented shape from local data; NULL cost passes through as `null` with `unpriced_calls` |
| L6 | **Statistics per section (frontend, mocks only).** Make the Statistics tab section-aware, following "Statistics per panel section": AI Content columns, Video Generation columns, and "In progress" for AI Influencer. Each section's mock data moves to the ledger's shapes: cost per post, video and run; "not recorded"; "≥ $X, N not priced". Also update the System Status mocks for provider health | `mini-apps` | L1 schema | Build passes; each section's Statistics shows only its own pipeline; mocks match the views' columns |

**Order:** L0 → L1 → L2, L3, L4 and L7 in parallel (separate files and systems) → L5. L6 can follow
L1, and once L7 exists it can switch from mocks to the local API.

**Before L0:** nothing more is needed for reading; the n8n connector already works. The collector
later needs an n8n API key, stored as an n8n credential. Ideally,
rotate the hard-coded Supabase key first (0.3), so the baseline export never handles a live key.

## Verification

- L1: re-sending a payload twice adds no rows and leaves the cost fields unchanged; an unpriced
  call leaves cost NULL and raises `unpriced_calls`; anon gets nothing; the worked example's
  numbers come out exactly; and `recompute_costs()` matches the stored fields.
- L5: run `recompute_costs()` against production as a check. Every `total_cost_usd` should be
  unchanged, and Σ `runs.total_cost_usd` = Σ `steps.cost_usd`.
- L3 and L4: fixture tests pass, and the real test runs appear in `runs` and `items` with their
  costs filled in.
- L4: the diff of the six production workflows against `baseline/` is empty (collector) or only
  adds ledger nodes (inline).
- L5: per-provider weekly totals reconcile with billing; the copied run count equals
  `video_agent_runs`; no rollup shows 0 for unrecorded cost.

## Appendix: rest of the panel (on hold for the AI Engineer)

- **Backend shape is fixed by the platform.** The mini-app CSP blocks external fetch, so the API is
  a Cloud Run service (`--no-allow-unauthenticated`) reached as
  `/api/mini-app-proxy/xpn-ai-content/…`. The ATT proxy handles Okta and forwards
  `X-Forwarded-User`, and a Mini-Apps Service Desk ticket registers it. The cloud environment is
  not set up yet.
- **D1, where backend code lives (for the team):**
  - A. `video-mcp_new`: next to the pipeline code, no extra setup; but it's an agent workspace under
    a personal GitHub account, with no service CI.
  - B. A new org repo: clean ownership, CI and deploy; but it needs creation and approval first.
  - C. `apps/xpn-ai-content/backend/` in mini-apps: one PR for both; but the new-app quality gate
    (Knip) would likely flag server files, and the apps that use this layout predate the gate.
  - Recommendation: A for the ledger now, and B before the service grows.
- **Cloud setup (Phase 0.5), when it's time:**
  1. Cloud Run and Secret Manager rights in the project.
  2. A runtime service account.
  3. Secrets by name: the ledger reader connection and the n8n API key.
  4. A test deploy.
  5. The Service Desk proxy ticket.
  6. A `/health` check through the proxy.
- **S1x frontend blockers, separate from the ledger:** add `.oxlintrc.json` and `knip.json` from
  `template/`, move TypeScript from `~5.8` to the template's `~7.0.2`, drop the unused
  `src/components/ui/*` files, and make the AI Influencer tabs "In progress" pages (all three
  sections stay).
