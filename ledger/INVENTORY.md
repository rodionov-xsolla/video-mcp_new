# XPN cost ledger: L0 inventory

Session L0, 2026-11-12. Read-only: no workflow was changed or executed, and nothing was written to
Supabase. This file is the input for L1 (schema) and L4 (n8n collector).

## Sources and how far to trust them

| Workflow | Id | Source used here | Version |
|---|---|---|---|
| Orchestrator | `hLCspmwIoGGalkGGDIIp1` | Live, n8n connector, 2026-11-12 | `dba2e3b2…`, updated 2026-09-15 |
| Content Provider | `ALobcKHwRGXxTkzG` | Live, n8n connector, re-exported 2026-11-13 after the Reddit snapshot change (see below) | `1d4f3543…`, updated 2026-11-13. The 2026-11-12 baseline (`ec44006e…`) is in commit `819de5c` |
| MEMES GENERATION | `j0vjj8EVv1kKCtzx` | Live, n8n connector, 2026-11-12 | `b28d339e…`, updated 2026-05-04 |
| Moderation | `yGyW6dWP3xfu446w` | **Local export only**: `~/Downloads/Xsolla ai content moderation (1).json`, file dated 2026-09-23. May be out of date. Not committed | `c0d60bc6…` |
| Publisher | `2SSIbhVPbKONRjcN` | **Not read.** No local export | — |
| Posting | `iJNExgMktpMdK8bk` | **Not read.** No local export. Makes no paid calls, per the plan | — |

- The connector only exposes workflows whose "Available in MCP" setting is on. Publisher,
  Moderation and Posting answer "Workflow not found". The Moderation export shows
  `availableInMCP: false`; Publisher and Posting are assumed to be the same.
- **Moderation's id has a capital W:** `yGyW6dWP3xfu446w`. The plan and the L0 brief have
  `yGyw6…`.
- The connector strips node credentials from its output, so the live exports have no credential
  names. The Moderation export names the OpenAI-type credential "OpenRouter account".
- The connector has no tool for reading executions. **Every "keeps `id`/`usage.cost`" answer
  below comes from the workflow config, not from an execution.** L4 confirms them on fixtures.
- Scrubbed live exports are in `baseline/` (see `baseline/README.md`).

## 1. Paid calls

Columns: **keeps id + cost** = does the node's saved output still hold OpenRouter's generation
`id` and `usage.cost`. **Purpose** uses the plan's `steps.purpose` names.

### Content Provider (live)

| Node | Node type | Provider | Model / product | Billing unit | Keeps id + cost | How known | Purpose |
|---|---|---|---|---|---|---|---|
| `Clean_the_article` | `@n8n/n8n-nodes-langchain.openAi` v1.8, text → message, JSON output | OpenRouter | `gpt-4.1-mini` (as configured) | tokens, cost reported | **No** | Config: "Simplify Output" is not set, so it defaults to on and the node keeps only `choices[0]` (`message`, `finish_reason`). Downstream reads `$('Clean_the_article').item.json.message.content.article`, which exists only in the simplified shape | clean |
| `Get_community` | same, temperature 0.5 | OpenRouter | `gpt-4.1-mini` | tokens | **No** | Config, same reason; downstream reads `.json.message.content` | community |
| `Analyze image` | same, image → analyze, base64 input, detail low | OpenRouter | `gpt-4.1-mini` | tokens | **No** | Config: simplify not set (default on) | vision |
| `Analyze Image` | same; runs once per gallery image inside `Gallery Analysis Loop1` | OpenRouter | `gpt-4.1-mini` | tokens | **No** | Config, same | vision |
| `Generate Embedding` | HTTP Request → `openrouter.ai/api/v1/embeddings` | OpenRouter | `text-embedding-ada-002` | tokens | **Probably**: the full JSON response is kept | Config. OpenRouter documents always-on `usage.cost` for chat and Responses calls only; embeddings need an execution to confirm | embed |
| `BrightData Scrape` | HTTP Request v3 → Web Scraper API `datasets/v3/scrape` (sync), dataset `gd_lyclm1571iy3mv57zw` | BrightData | Web Scraper API, used for facebook.com URLs (`Switch3`) | records | n/a | Config | scrape |
| `BrightData Scrape1`, `BrightData Scrape2` | progress poll and snapshot download, used when the sync scrape returns a `snapshot_id` | BrightData | — | not billed per call (records are billed once) | n/a | Config; billing basis from BrightData's pricing | scrape |
| `BrightData Reddit Scrape` | HTTP Request → `datasets/v3/trigger` (async), dataset `gd_lvz8ah06191smkebj4` | BrightData | Web Scraper API, reddit.com URLs | records | n/a | Config | scrape |
| `Get BrightData Reddit Snapshot` | snapshot poll in a loop: `Wait BrightData Reddit Snapshot` (90 s) → Get → `Is BrightData Snapshot Still Running?` (status `running` or `building` and `$runIndex` < 14) → back to the Wait. Up to 15 runs per execution (runIndex 0–14) | BrightData | — | not billed per call; records are counted from the run that returned them | n/a | Config (version `1d4f3543…`) | scrape |
| `HTTP Request2` | HTTP Request → `api.brightdata.com/request`, zone `web_unlocker1` | BrightData | Web Unlocker, for other sites | successful requests | n/a | Config | scrape |
| `TG parser` | HTTP Request → `telegram-parser.koka.team/summary` | koka.team service | t.me URLs | unknown | n/a | Config | scrape |
| `Create directory`, `Video upload link`, `Audio upload link` | HTTP Request → `api.ffmpeg-api.com` `/directory`, `/file` | ffmpeg-api.com | Reddit DASH video branch | GB-seconds (subscription quota); unknown whether these calls use any | n/a | Config | media_merge |
| `Upload video`, `Upload audio` | PUT to the pre-signed upload URL | ffmpeg-api.com storage | — | unknown | n/a | Config | media_merge |
| `Merge content` | `api.ffmpeg-api.com/ffmpeg/process` (video + audio merge) | ffmpeg-api.com | — | GB-seconds | n/a | Config | media_merge |
| `Probe Video` | `api.ffmpeg-api.com/ffprobe/analyze` | ffmpeg-api.com | Facebook/TG video branch | GB-seconds (unconfirmed) | n/a | Config | media_merge |
| `Compress Video` | `api.ffmpeg-api.com/ffmpeg/process` | ffmpeg-api.com | only when `Needs Compression?` is true | GB-seconds | n/a | Config | media_merge |

- Not paid, so not steps: Telegram sends, Reddit, Google Sheets, Supabase and Postgres nodes, and
  plain media downloads.
- Not reachable today: `koka video download`, `koka video download1`, `Get resolution`,
  `Get resolution1`, `Send a video`, `Send a video2` and `Every 30 seconds` are disabled.
  `Get a post1` and `Stop and Error2` have no incoming connection. Since version `1d4f3543…`,
  neither does `Wait BrightData Reddit Snapshot Retry` (and with it
  `Get BrightData Reddit Snapshot Retry`).
- The plan's purpose list has no probe or compress category, so all ffmpeg calls map to
  `media_merge` here. L1 may want `media_process` instead.

### MEMES GENERATION (live)

| Node | Node type | Provider | Model | Billing unit | Keeps id + cost | How known | Purpose |
|---|---|---|---|---|---|---|---|
| `Text creator model1` | `@n8n/n8n-nodes-langchain.openAi` v1.8, message | OpenRouter (per plan; credential not visible) | `chatgpt-4o-latest` (as configured) | tokens | **No** | Config: simplify not set (default on); `Create a row2` reads `$('Text creator model1').item.json.message.content` | localize |
| `Add pic gen` | HTTP Request → `openrouter.ai/api/v1/chat/completions` | OpenRouter | `google/gemini-3-pro-image-preview` | image + tokens, cost reported | **Yes** (`id`); `usage.cost` per OpenRouter docs | Config: full JSON response kept; OpenRouter documents `usage` (with `cost`) as always included | meme_translate |
| `Gemini Translate Image` | HTTP Request → OpenRouter chat/completions | OpenRouter | `google/gemini-2.5-flash-image` | image + tokens | **Yes** (`id`); `usage.cost` per docs | Config, same | meme_translate |

- `Text creator model1` runs once per channel (one `Start loop1` iteration each), on the MEME
  branch.
- `Add pic gen` runs only when the meme's text language differs from the channel's (`If3`): at
  most once per channel.
- `Gemini Translate Image` belongs to the other branch (input is not a MEME). It is started from
  Moderation's "translate_approved" button and runs once per image in the post's `pic_url`.
- `make sora request`, `make sora request2`, `check progress` and `get picture` call
  `private.lab.koka.team:6789`, but nothing connects into `If5`, so that branch never runs.
- `retryOnFail` is on for `Gemini Translate Image`. n8n saves only the last attempt's output, so a
  billed attempt that failed inside a retry leaves no trace in the execution.

### Moderation (local export of 2026-09-23, not live)

| Node | Node type | Provider | Model | Billing unit | Keeps id + cost | How known | Purpose |
|---|---|---|---|---|---|---|---|
| `Message a model2` | `@n8n/n8n-nodes-langchain.openAi` **v2** (Responses API) | OpenRouter (credential "OpenRouter account") | `gpt-5` | tokens | **Unknown** | Config: simplify not set; downstream reads `$json.output[0].content[0].text`, which both the simplified and the full Responses shapes have | ai_edit |
| `Add pic gen` | HTTP Request → OpenRouter chat/completions | OpenRouter | `google/gemini-3-pro-image-preview` | image + tokens | **Yes** (`id`); `usage.cost` per docs | Config: full JSON response kept | ai_edit (picture edit) |
| `Message a model` | `@n8n/n8n-nodes-langchain.openAi` v1.8, message | OpenRouter | `gpt-5-mini` | tokens | **No** | Config: simplify default; downstream reads `.json.message.content` | localize (see note) |

- `Message a model2` is the "AI edit" button: the moderator types a prompt, gpt-5 rewrites the
  post.
- `Add pic gen` is the "pic edit" button.
- `Message a model` is not in the plan. When a moderator opens a post whose language is not
  Russian (`If1`), gpt-5-mini translates it for the moderator. It runs every time such a post is
  shown, so it is moderation overhead rather than localization. L1 may want a
  `moderator_translate` purpose.
- "translate_approved" calls MEMES GENERATION, so that cost lands in a separate MEMES execution,
  linked by post id.
- Moderation also calls "Giveaway Moderator Flow" (`p6SDGeJ1Ai3rRxTm`), which is outside the
  ledger.
- Moderation is a Telegram-trigger workflow: every button press is an execution, and most make no
  paid call. The collector should skip executions in which no mapped node ran.

### Publisher (not read)

From the plan and the docs only: `Text creator model` once per channel, and one image-generation
request. Node names, node types, models and output settings are **unverified**. If `Text creator
model` is the same node type as MEMES's `Text creator model1` (likely, since MEMES looks copied
from Publisher), it keeps no `id` or `usage`.

### Key finding: most model calls drop their cost

Six of the nine model nodes read so far are `@n8n/n8n-nodes-langchain.openAi` nodes with
"Simplify Output" on (the default): `Clean_the_article`, `Get_community`, both `Analyze image`
nodes, `Text creator model1` and Moderation's `Message a model`. Their saved output has no `id`,
no `usage` and no `model`, so neither a collector nor inline ledger nodes can read their cost.
Publisher's `Text creator model` is probably the seventh.

Turning "Simplify Output" off is **not** a settings-only change. The output shape moves from
`message.content` to `choices[0].message.content`, and every downstream expression that reads it
would break. Options:

1. **Estimate now** (recommended for L4). Tokens ≈ characters ÷ 4 for the prompt and the output,
   times the model's OpenRouter price. The prompt template is in the workflow and the inserted
   fields and the output are in the execution. Prices come from OpenRouter's `GET /api/v1/models`,
   versioned in git. Rows get `cost_source = 'estimated'`, and `steps.model` comes from the config.
2. **Reconcile in L5.** Compare the ledger's OpenRouter totals per day and per model with
   OpenRouter's own usage figures. A separate OpenRouter key per workflow would make this exact per
   workflow; that is a credential change and needs your approval.
3. **Fix later.** Turning off "Simplify Output" and updating the downstream expressions is a
   pipeline change for the AI Engineer's list.

## 2. Item linkage

| Unit | Table | Node that yields the id | Notes |
|---|---|---|---|
| lead | `xsolla_ai_content_inbox` | Content Provider `Extract Inbox Item ID` → `json.id` | Same as the trigger item from the Orchestrator's `Select Top 1 Inbox Item`. Inbox statuses written: `PENDING`, `TAKEN`, `PROCESSED`, `RETRY_CHATGPT_FAILURE`, `INVALID` |
| story | `xsolla_ai_content_provider` | Content Provider `Save the Post` → `json.id` of every output item of every run | Usually one. When an item has both image and video media, `Aggregate Media Metadata` runs twice and so does `Save the Post`: two stories |
| story → lead | — | **No column links them.** `Save the Post` writes no inbox id | Inside one execution the link is certain (same execution). For backfill (L2), match `content_provider."URL"` to `inbox.url` |
| post | `xsolla_ai_posted_content_base` | MEMES `Create a row2` → `json.id` (status `wait moderation`); `Create a row3` → `json.id` (status `error`) | Row carries `news_id` (story id), `channel_id`, `channel_type`, `language`, `country` |
| post | `xsolla_ai_posted_content_base` | Publisher: `Create a row` per the plan | Unverified |
| post (moderation) | `xsolla_ai_posted_content_base` | Moderation `Get Last Moderation Record*` → `row_id` (from `moderation_data`); `Get a row2` → `id` for AI edit | From the Sep export |
| post (image translation) | `xsolla_ai_posted_content_base` | MEMES `Start trigger` → `json.id`, on the non-MEME branch (`Update a row` filters on it) | Started by Moderation "translate_approved" |

**Pairing `Text creator model` calls with their `Create a row` (MEMES, from config):**
- `Start loop1` is a Loop Over Items node (v3) with no batch size set, so it uses the default of
  1. Each iteration handles one channel: `Text creator model1` run *k* → … → `Create a row2` (or
  `Create a row3` on error).
- Plain run-index matching breaks when a channel errors, because that iteration ends in
  `Create a row3` instead. So the collector should follow n8n's lineage instead:
  - each node run in `runData` names the run it came from (`source[0].previousNode` and
    `previousNodeRun`);
  - each item carries `pairedItem`.
- Walk back from each `Create a row2`/`row3` run to its `Text creator model1` run, and to the
  `Add pic gen` run if there was one. `Create a row2` itself reads
  `$('Text creator model1').item`, so n8n already keeps that lineage.
- Publisher is unverified. L4 checks it on a real execution.

## 3. Outcome mapping

### Content Provider

| Node reached | Kind | Run status | Outcome |
|---|---|---|---|
| `Disturbing Post` | Stop and Error | rejected | `disturbing` |
| `Commercial Post` | Stop and Error | rejected | `commercial` (new; not in the plan's list) |
| `Duplicated Post` (similarity ≥ 0.925 within 2 days, same game) | Stop and Error | rejected | `duplicate` |
| `Forbidden Game Tag` (not in the titles whitelist sheet) | Stop and Error | rejected | `forbidden_tag` |
| `ChatGPT Error`, after `Retry Inbox Item` sets `RETRY_CHATGPT_FAILURE` | Stop and Error | failed | `model_error`. The lead goes back into the queue, so one lead can have several runs |
| `ChatGPT Error1` ("Crawl FB parser error", Facebook snapshot error) | Stop and Error | failed | `scrape_failed` |
| `Mark Reddit Fallback as Invalid`, after `Discard Reddit Fallback` | normal end | rejected | `invalid_source` (Reddit fallback without a usable image; inbox `INVALID`) |
| `Do Nothing, Test Execution` (`$execution.mode` ≠ production) | normal end | skip | test run: not recorded |
| `Save the Post` → `Mark Inbox Item as Processed` | normal end | succeeded | `story_saved` |
| `Webhook` → `Save Pending Item in Inbox` | normal end | skip | RSS ingest: no paid calls, not recorded |
| any uncaught node error | n8n status `error` | failed | `error`, with `lastNodeExecuted` and the error message |

### MEMES GENERATION

| Node reached | Run status | Outcome |
|---|---|---|
| `Create a row2` for every channel, then `Update a row4` (story → `posted`) | succeeded | `posts_created` |
| `Create a row3` for some channels (post row with status `error`, after `Error Notification2`) | succeeded, partly | the run goes on; the failed channel is a post with status `error` |
| `Set status wait moderation` (translation branch done) | succeeded | `translated` |
| `Stop on Error` (translation branch) | failed | `translation_failed`; the post stays in `translation` |

### Moderation (Sep export)

- Moderation writes post states, not run outcomes. The ledger reads post status live from
  `xsolla_ai_posted_content_base`.
- States written: `on moderation`, `approved`, `decline`, `posted`, `error`, `translation`,
  `wait moderation`.
- Run outcome for paid executions: `ai_edit`, `pic_edit` or `moderator_translate`.

### Not found anywhere read so far

`source_mismatch` and `no_channel` appear in neither Content Provider nor MEMES nor the Moderation
export. They probably live in Publisher, which L4 has to read.

### Two facts from the configs

- **A moderator Decline writes `decline`** (lowercase, not "declined") to
  `xsolla_ai_posted_content_base.status`:
  - path: `Callback Router` output "decline" → `prepare_data_for_nocodb2` (sets `status: "decline"`)
    → `Update a row4`;
  - source: the 2026-09-23 Moderation export, not the live workflow.
- **`xsolla_ai_posted_content_base` has `created_at`, and also `status_updated_at`:**
  - the live Orchestrator's `Execute a SQL query` filters on
    `COALESCE(status_updated_at, created_at)`;
  - no workflow writes `created_at`, so a database default fills it (confirm in the schema at L1);
  - stories have `published_at`, filled the same way and used by `Find the most similar Post`.

## 4. Execution settings and the collector-vs-inline decision

| Workflow | Save successful | Save failed | Save manual | Save progress | Source |
|---|---|---|---|---|---|
| Orchestrator | default | default | default | default | live `settings`: only `executionOrder`, `availableInMCP` |
| Content Provider | default | default | default | default | live `settings`: `executionOrder`, `callerPolicy`, `availableInMCP` |
| MEMES GENERATION | default | default | default | default | live, same |
| Moderation | default | default | default | default | Sep export, same |
| Publisher | unknown | unknown | unknown | unknown | not readable |

- "default" means the workflow does not override anything, so the instance settings apply.
- **Instance settings**, read from `workflow.xsolla.com/rest/settings` on 2026-11-13 by the
  planning session (the connector cannot see them). n8n 2.5.2, queue mode:

  | Setting | Value |
  |---|---|
  | `saveDataSuccessExecution` | `all` |
  | `saveDataErrorExecution` | `all` |
  | `saveManualExecutions` | `true` |
  | Pruning | on: max age 336 h (14 days), max count 250,000 |
  | `executionTimeout` / `maxExecutionTimeout` | -1 / 3600 s |
  | concurrency | -1 |

**Decision: A, the collector.** Rule 1 of the plan is met at instance level.
- Why:
  - Successful and failed executions are saved with their data, and kept for 14 days.
  - No workflow read so far overrides saving.
  - The 250,000-execution cap is far above the instance's daily volume as far as it is known: the
    Orchestrator's 1,440 executions a day plus the sub-workflows and Moderation presses.
  - The collector is the only option that also captures failed runs and rejected leads.
  - It changes nothing in production.
  - The cost gap in Section 1 hits inline nodes just as hard, so it is no argument for B.
- What L4 still checks, with the API key:
  1. Publisher's own `settings`: it is the one paid workflow not yet read, and a workflow can
     override the instance default.
  2. Each of the four workflows has `success` and `error` executions in
     `GET /api/v1/executions`, and the oldest is about 14 days old.
  3. If Publisher turns out to override saving, rule 2 applies: "Save successful production
     executions" gets turned on for it, with your approval. B only if that can't be changed.
- Collector notes:
  - Sub-workflow executions started by the Orchestrator have mode `integrated`. Skip only
    `manual` executions (and the test webhook), not `integrated`.
  - The Orchestrator, Content Provider, Publisher and Posting calls use
    `waitForSubWorkflow: false`. Each is its own execution, read by `workflowId`.
  - A Content Provider execution on the Reddit path sits in `waiting` status between snapshot
    checks: 90 s each, up to 15 checks, so up to about 22 minutes. Read only finished executions
    (success, error, canceled, crashed), and move the watermark on `stoppedAt`, not `startedAt`.
    Otherwise a run that started before the watermark and finished after it is skipped.
  - `Get BrightData Reddit Snapshot` can appear up to 15 times in one execution's `runData`. Map
    every run, and count records only from the run that returned them.

## 5. Fixtures: blocked

The n8n connector offers only `search_workflows`, `get_workflow_details` and `execute_workflow`. It
cannot list or read executions, so no fixtures were saved. `collector-n8n/fixtures/` holds only a
README.

What unblocks it:
1. **An n8n API key** for `workflow.xsolla.com`:
   - create it under Settings → n8n API, with read access to workflows and executions if the
     instance offers scopes;
   - keep it in an environment variable, never in the repo;
   - L4 needs it anyway, stored as an n8n credential for the collector.
2. Then for each of the four workflows:
   - fetch one success, one rejected or stopped and one failed execution:
     `GET /api/v1/executions?workflowId=<id>&status=<success|error>&includeData=true&limit=…`;
   - run each through `python3 baseline/scrub.py IN OUT`;
   - blank personal data before committing: post text, Telegram user and chat ids, moderator
     names. The scrub script does not do that part.
3. With the same key, export Publisher, Moderation and Posting:
   - `GET /api/v1/workflows/<id>`, scrubbed into `baseline/`;
   - that completes the six baselines without turning on MCP access.

Exporting from the n8n UI is not a real alternative. n8n has no whole-execution download; a
person could copy each node's output from the execution view, which is slow and easy to get wrong.

## 6. Prices (non-model calls)

See `collector-n8n/prices.json`.
- **BrightData:**
  - Web Scraper API $1.50 per 1,000 records;
  - Web Unlocker $1.50 per 1,000 successful requests;
  - both pay-as-you-go list prices, unverified.
- **ffmpeg-api.com:** a monthly subscription metered in GB-seconds, with no per-call price, so it
  is `null`.
- **koka.team parser:** unknown, `null`.

Open questions:
- Which BrightData plan the account is on.
- Which ffmpeg-api.com plan is used, and whether its cost should be spread over calls.
- Whether koka.team services cost anything.

## 7. Scope: Art generator and cosplay generator

The same instance runs two more active scheduled workflows that make model and image calls:
- "XSOLLA Art generator pipeline" (`PpzIpplWiA40Swzq`): `Prompt generating`, `Text generating`,
  `Style generator`, `Embedding`, `PIC Generating`;
- "XSOLLA cosplay generator pipeline" (`8zy4KFc7lc0j39sm`): `Prompt gen`, `Text gen`,
  `Style gen`, `Embedding`, `1st pic gen`, `Add pic gen` ×3.

**Answer: pending.** Asked on 2026-11-12; the question was cut off when the app closed. Until
answered, they stay out of the node map and count as known untracked spend.

## 8. Corrections to the plan

- Moderation's id is `yGyW6dWP3xfu446w`, with a capital W.
- The plan says `ledger/collector/prices.json`; this session used `ledger/collector-n8n/` as the
  brief asked. L4 should keep one of the two.
- Outcomes not in the plan's list: `commercial`, `invalid_source`, `model_error`,
  `scrape_failed`.
- Content Provider also has an RSS webhook path (`Webhook` → `Save Pending Item in Inbox`). Those
  executions make no paid calls.
- MEMES calls two image models through OpenRouter HTTP nodes. Its "sora" branch is dead code.
- **Hard-coded secrets:** besides the Supabase service-role key in two MEMES nodes, the Moderation
  export has a Telegram bot token written into five nodes (`HTTP Request5`,
  `Remove Moderation Buttons`, `Prepare Telegram Post Request`, `Code in JavaScript3`,
  `Code in JavaScript8`). The value is not reproduced anywhere in this repo. Both should be
  rotated and moved into credentials.
