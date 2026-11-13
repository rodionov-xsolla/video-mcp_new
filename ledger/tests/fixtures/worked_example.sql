-- The plan's worked example as record_run payloads. Included with \ir by the tests; creates
-- temporary objects only, and sends nothing until a test calls pg_temp.send(name).
--
--   cp_812  Content Provider: lead 812 -> story 455, five calls, 0.0090
--   pub_1   Publisher: image for story 455 (0.0400) + three posts (RU 0.0012, EN 0.0011, Discord 0.0010)
--   pub_2   a later Publisher run adds a fourth post (X 0.0009), which changes every post's share
--   cp_813  Content Provider: lead 813 rejected as a duplicate, 0.0052, no story
--   vid_1   video: 6 images at 0.08, 5 clips of 5 s at 0.084/s, one billed clip that failed and
--           was redone (0.42), one TTS call with no price

create temp table fx (name text primary key, body jsonb not null);

insert into fx (name, body) values
('cp_812', $j${
  "run": {"pipeline": "content", "workflow": "content_provider", "external_id": "cp-812",
          "workflow_version": "1d4f3543", "status": "succeeded", "outcome": "story_saved", "item": "lead",
          "started_at": "2026-11-13T10:00:00Z", "finished_at": "2026-11-13T10:02:00Z"},
  "items": [
    {"ref": "lead", "kind": "lead", "source_table": "xsolla_ai_content_inbox", "source_id": "812",
     "game": "PALWORLD", "title": "PALWORLD Reddit post"},
    {"ref": "story", "kind": "story", "parent": "lead", "source_table": "xsolla_ai_content_provider",
     "source_id": "455", "game": "PALWORLD"}
  ],
  "steps": [
    {"idempotency_key": "n8n:cp-812:BrightData Reddit Scrape:0:0", "node": "BrightData Reddit Scrape",
     "provider": "brightdata", "purpose": "scrape", "cost_source": "computed",
     "unit": "records", "units": 2, "unit_price_usd": 0.0015},
    {"idempotency_key": "n8n:cp-812:Clean_the_article:0:0", "node": "Clean_the_article",
     "provider": "openrouter", "model": "openai/gpt-4.1-mini", "purpose": "clean",
     "cost_usd": 0.0021, "cost_source": "estimated", "unit": "tokens", "units_in": 1800, "units_out": 600},
    {"idempotency_key": "n8n:cp-812:Get_community:0:0", "node": "Get_community",
     "provider": "openrouter", "model": "openai/gpt-4.1-mini", "purpose": "community",
     "cost_usd": 0.0004, "cost_source": "estimated", "unit": "tokens"},
    {"idempotency_key": "n8n:cp-812:Generate Embedding:0:0", "node": "Generate Embedding",
     "provider": "openrouter", "model": "openai/text-embedding-ada-002", "purpose": "embed",
     "cost_usd": 0.0001, "cost_source": "reported", "unit": "tokens"},
    {"idempotency_key": "n8n:cp-812:Analyze image:0:0", "node": "Analyze image",
     "provider": "openrouter", "model": "openai/gpt-4.1-mini", "purpose": "vision",
     "cost_usd": 0.0034, "cost_source": "estimated", "unit": "tokens"}
  ]}$j$),

('pub_1', $j${
  "run": {"pipeline": "content", "workflow": "publisher", "external_id": "pub-1",
          "status": "succeeded", "outcome": "posts_created", "item": "story",
          "started_at": "2026-11-13T10:05:00Z", "finished_at": "2026-11-13T10:06:00Z"},
  "items": [
    {"ref": "story", "kind": "story", "source_table": "xsolla_ai_content_provider", "source_id": "455"},
    {"ref": "p_ru", "kind": "post", "parent": "story", "source_table": "xsolla_ai_posted_content_base",
     "source_id": "7001", "game": "PALWORLD", "channel_id": "tg_ru", "channel_type": "telegram", "language": "ru"},
    {"ref": "p_en", "kind": "post", "parent": "story", "source_table": "xsolla_ai_posted_content_base",
     "source_id": "7002", "game": "PALWORLD", "channel_id": "tg_en", "channel_type": "telegram", "language": "en"},
    {"ref": "p_dc", "kind": "post", "parent": "story", "source_table": "xsolla_ai_posted_content_base",
     "source_id": "7003", "game": "PALWORLD", "channel_id": "discord_main", "channel_type": "discord", "language": "en"}
  ],
  "steps": [
    {"idempotency_key": "n8n:pub-1:Image request:0:0", "item": "story", "node": "Image request",
     "provider": "openrouter", "model": "google/gemini-3-pro-image-preview", "purpose": "image_gen",
     "cost_usd": 0.0400, "cost_source": "reported", "unit": "images", "units": 1},
    {"idempotency_key": "n8n:pub-1:Text creator model:0:0", "item": "p_ru", "node": "Text creator model",
     "provider": "openrouter", "model": "openai/chatgpt-4o-latest", "purpose": "localize",
     "cost_usd": 0.0012, "cost_source": "estimated", "unit": "tokens"},
    {"idempotency_key": "n8n:pub-1:Text creator model:1:0", "item": "p_en", "node": "Text creator model",
     "provider": "openrouter", "model": "openai/chatgpt-4o-latest", "purpose": "localize",
     "cost_usd": 0.0011, "cost_source": "estimated", "unit": "tokens"},
    {"idempotency_key": "n8n:pub-1:Text creator model:2:0", "item": "p_dc", "node": "Text creator model",
     "provider": "openrouter", "model": "openai/chatgpt-4o-latest", "purpose": "localize",
     "cost_usd": 0.0010, "cost_source": "estimated", "unit": "tokens"}
  ]}$j$),

('pub_2', $j${
  "run": {"pipeline": "content", "workflow": "publisher", "external_id": "pub-2",
          "status": "succeeded", "outcome": "posts_created", "item": "story",
          "started_at": "2026-11-13T11:00:00Z", "finished_at": "2026-11-13T11:01:00Z"},
  "items": [
    {"ref": "story", "kind": "story", "source_table": "xsolla_ai_content_provider", "source_id": "455"},
    {"ref": "p_x", "kind": "post", "parent": "story", "source_table": "xsolla_ai_posted_content_base",
     "source_id": "7004", "game": "PALWORLD", "channel_id": "x_main", "channel_type": "x", "language": "en"}
  ],
  "steps": [
    {"idempotency_key": "n8n:pub-2:Text creator model:0:0", "item": "p_x", "node": "Text creator model",
     "provider": "openrouter", "model": "openai/chatgpt-4o-latest", "purpose": "localize",
     "cost_usd": 0.0009, "cost_source": "estimated", "unit": "tokens"}
  ]}$j$),

('cp_813', $j${
  "run": {"pipeline": "content", "workflow": "content_provider", "external_id": "cp-813",
          "status": "rejected", "outcome": "duplicate", "item": "lead",
          "started_at": "2026-11-13T10:10:00Z", "finished_at": "2026-11-13T10:11:00Z"},
  "items": [
    {"ref": "lead", "kind": "lead", "source_table": "xsolla_ai_content_inbox", "source_id": "813", "game": "PALWORLD"}
  ],
  "steps": [
    {"idempotency_key": "n8n:cp-813:BrightData Reddit Scrape:0:0", "node": "BrightData Reddit Scrape",
     "provider": "brightdata", "purpose": "scrape", "cost_source": "computed",
     "unit": "records", "units": 2, "unit_price_usd": 0.0015},
    {"idempotency_key": "n8n:cp-813:Clean_the_article:0:0", "node": "Clean_the_article",
     "provider": "openrouter", "model": "openai/gpt-4.1-mini", "purpose": "clean",
     "cost_usd": 0.0021, "cost_source": "estimated", "unit": "tokens"},
    {"idempotency_key": "n8n:cp-813:Generate Embedding:0:0", "node": "Generate Embedding",
     "provider": "openrouter", "model": "openai/text-embedding-ada-002", "purpose": "embed",
     "cost_usd": 0.0001, "cost_source": "reported", "unit": "tokens"}
  ]}$j$),

('vid_1', $j${
  "run": {"pipeline": "video", "workflow": "video_agent", "external_id": "20261113-101500-4242",
          "status": "succeeded", "outcome": "approved_final", "item": "video",
          "started_at": "2026-11-13T10:15:00Z", "finished_at": "2026-11-13T10:55:00Z"},
  "items": [
    {"ref": "video", "kind": "video", "pipeline": "video", "source_table": "video_agent",
     "source_id": "20261113-101500-4242", "game": "PALWORLD", "format": "character-story"}
  ],
  "steps": [
    {"idempotency_key": "video:img-1:1", "provider": "fal", "model": "nano-banana-2", "purpose": "image",
     "cost_source": "computed", "unit": "images", "units": 1, "unit_price_usd": 0.08},
    {"idempotency_key": "video:img-2:1", "provider": "fal", "model": "nano-banana-2", "purpose": "image",
     "cost_source": "computed", "unit": "images", "units": 1, "unit_price_usd": 0.08},
    {"idempotency_key": "video:img-3:1", "provider": "fal", "model": "nano-banana-2", "purpose": "image",
     "cost_source": "computed", "unit": "images", "units": 1, "unit_price_usd": 0.08},
    {"idempotency_key": "video:img-4:1", "provider": "fal", "model": "nano-banana-2", "purpose": "image",
     "cost_source": "computed", "unit": "images", "units": 1, "unit_price_usd": 0.08},
    {"idempotency_key": "video:img-5:1", "provider": "fal", "model": "nano-banana-2", "purpose": "image",
     "cost_source": "computed", "unit": "images", "units": 1, "unit_price_usd": 0.08},
    {"idempotency_key": "video:img-6:1", "provider": "fal", "model": "nano-banana-2", "purpose": "image",
     "cost_source": "computed", "unit": "images", "units": 1, "unit_price_usd": 0.08},
    {"idempotency_key": "video:clip-1:1", "provider": "fal", "model": "kling-v3-standard", "purpose": "clip",
     "ok": false, "error_message": "PAID_RETRY_REQUIRED", "attempt": 1,
     "cost_source": "computed", "unit": "seconds", "units": 5, "unit_price_usd": 0.084},
    {"idempotency_key": "video:clip-1:2", "provider": "fal", "model": "kling-v3-standard", "purpose": "clip",
     "attempt": 2, "is_retry": true,
     "cost_source": "computed", "unit": "seconds", "units": 5, "unit_price_usd": 0.084},
    {"idempotency_key": "video:clip-2:1", "provider": "fal", "model": "kling-v3-standard", "purpose": "clip",
     "cost_source": "computed", "unit": "seconds", "units": 5, "unit_price_usd": 0.084},
    {"idempotency_key": "video:clip-3:1", "provider": "fal", "model": "kling-v3-standard", "purpose": "clip",
     "cost_source": "computed", "unit": "seconds", "units": 5, "unit_price_usd": 0.084},
    {"idempotency_key": "video:clip-4:1", "provider": "fal", "model": "kling-v3-standard", "purpose": "clip",
     "cost_source": "computed", "unit": "seconds", "units": 5, "unit_price_usd": 0.084},
    {"idempotency_key": "video:clip-5:1", "provider": "fal", "model": "kling-v3-standard", "purpose": "clip",
     "cost_source": "computed", "unit": "seconds", "units": 5, "unit_price_usd": 0.084},
    {"idempotency_key": "video:tts:1", "provider": "elevenlabs", "purpose": "tts"}
  ]}$j$);

create function pg_temp.send(p_name text) returns jsonb
language sql as $$ select ledger.record_run(body) from fx where name = p_name $$;

create function pg_temp.item(p_source_id text) returns ledger.items
language sql as $$ select * from ledger.items where source_id = p_source_id $$;

create function pg_temp.run(p_external_id text) returns ledger.runs
language sql as $$ select * from ledger.runs where external_id = p_external_id $$;

-- Every stored cost field, for "nothing changed" comparisons.
create temp view cost_fields as
select 'item' as kind, id, own_cost_usd as a, upstream_share_usd as b, total_cost_usd as c,
       unpriced_calls as d
  from ledger.items
union all
select 'run', id, total_cost_usd, failed_attempts_cost_usd, null, unpriced_calls
  from ledger.runs;
