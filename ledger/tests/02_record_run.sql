-- record_run: idempotent re-sends, NULL-not-0 cost fields, unpriced_calls, computed costs,
-- status handling and payload validation.
begin;
create extension if not exists pgtap with schema extensions;
\ir fixtures/worked_example.sql
select plan(33);

-- First send
select is(pg_temp.send('cp_812') ->> 'steps_inserted', '5', 'first send inserts five steps');
select is((select count(*)::integer from ledger.items), 2, 'lead and story created');
select is((pg_temp.item('455')).parent_id, (pg_temp.item('812')).id, 'story is linked to its lead');
select is(
  (select cost_usd from ledger.steps where idempotency_key = 'n8n:cp-812:BrightData Reddit Scrape:0:0'),
  0.0030::numeric, 'computed cost = units x unit_price_usd');

-- Re-send: no new rows, cost fields unchanged
create temp table before_resend as select * from cost_fields;
select is(pg_temp.send('cp_812') ->> 'steps_inserted', '0', 're-send inserts no steps');
select is(pg_temp.send('cp_812') ->> 'steps_skipped', '5', 're-send skips all five steps');
select is((select count(*)::integer from ledger.steps), 5, 'still five steps');
select is((select count(*)::integer from ledger.runs), 1, 'still one run');
select is((select count(*)::integer from ledger.items), 2, 'still two items');
select is(
  (select count(*)::integer from (
     (select * from before_resend except select * from cost_fields)
     union all
     (select * from cost_fields except select * from before_resend)) d),
  0, 're-send leaves every cost field unchanged');

-- A late "running" never moves a finished run back
do $$ begin perform ledger.record_run(
  '{"run": {"pipeline": "content", "workflow": "content_provider", "external_id": "cp-812", "status": "running"}}'); end $$;
select is((pg_temp.run('cp-812')).status, 'succeeded', 'a late "running" keeps the run succeeded');

-- NULL means unknown, never 0
do $$ begin perform ledger.record_run($j${
  "run": {"pipeline": "content", "workflow": "moderation_ai_edit", "external_id": "m-1", "status": "succeeded",
          "item": "post"},
  "items": [{"ref": "post", "kind": "post", "source_table": "xsolla_ai_posted_content_base", "source_id": "9901"}],
  "steps": [
    {"idempotency_key": "m-1:a", "provider": "koka_team", "purpose": "ai_edit"},
    {"idempotency_key": "m-1:b", "provider": "koka_team", "purpose": "ai_edit"}
  ]}$j$); end $$;
select is((select cost_usd from ledger.steps where idempotency_key = 'm-1:a'), null::numeric, 'an unpriced call keeps cost NULL');
select is((select cost_source from ledger.steps where idempotency_key = 'm-1:a'), 'unknown', 'an unpriced call has cost_source unknown');
select is((pg_temp.run('m-1')).unpriced_calls, 2, 'unpriced calls are counted on the run');
select is((pg_temp.run('m-1')).total_cost_usd, 0::numeric, 'run total holds the known part (nothing known)');
select is((pg_temp.item('9901')).unpriced_calls, 2, 'unpriced calls are counted on the item');

-- Partially priced: total = known part, unpriced counted
select is((pg_temp.run('cp-812')).total_cost_usd, 0.0090::numeric, 'fully priced run total');
select is((pg_temp.run('cp-812')).unpriced_calls, 0, 'fully priced run has no unpriced calls');

-- A story created but not yet worked on: own cost unknown, total = its share
select is((pg_temp.item('455')).own_cost_usd, null::numeric, 'story with no calls yet has own cost NULL');
select is((pg_temp.item('455')).total_cost_usd, 0.0090::numeric, 'its total is its share of the lead');

-- A legacy run whose calls were never captured: every cost field NULL
do $$ begin perform ledger.record_run($j${
  "run": {"pipeline": "video", "workflow": "video_agent", "external_id": "legacy-77", "status": "succeeded",
          "source": "legacy_copy", "cost_recorded": false, "item": "v"},
  "items": [{"ref": "v", "kind": "video", "source_table": "video_agent_runs", "source_id": "77"}]
  }$j$); end $$;
select is((pg_temp.run('legacy-77')).total_cost_usd, null::numeric, 'legacy run total is NULL, not 0');
select is((pg_temp.run('legacy-77')).unpriced_calls, null::integer, 'legacy run unpriced_calls is NULL');
select is((pg_temp.item('77')).total_cost_usd, null::numeric, 'legacy video total is NULL, not 0');

-- Failed and superseded calls
do $$ begin perform ledger.record_run($j${
  "run": {"pipeline": "content", "workflow": "memes", "external_id": "mm-1", "status": "failed",
          "error_message": "timeout"},
  "steps": [
    {"idempotency_key": "mm-1:a", "provider": "openrouter", "purpose": "meme_translate", "ok": false,
     "cost_usd": 0.03, "cost_source": "reported"},
    {"idempotency_key": "mm-1:b", "provider": "openrouter", "purpose": "meme_translate", "superseded": true,
     "cost_usd": 0.02, "cost_source": "reported"},
    {"idempotency_key": "mm-1:c", "provider": "openrouter", "purpose": "meme_translate",
     "cost_usd": 0.01, "cost_source": "reported"}
  ]}$j$); end $$;
select is((pg_temp.run('mm-1')).failed_attempts_cost_usd, 0.05::numeric, 'failed + superseded calls make up failed_attempts_cost_usd');
select is((pg_temp.run('mm-1')).total_cost_usd, 0.06::numeric, 'failed attempts stay inside the total');

-- Validation: the whole payload is refused, nothing is written
select throws_ok($$select ledger.record_run('{"items": []}')$$, '22023', null, 'payload without a run is refused');
select throws_ok(
  $$select ledger.record_run('{"run": {"pipeline": "content", "workflow": "x", "external_id": "v1", "status": "succeeded"},
     "items": [{"ref": "p", "kind": "post", "parent": "nope", "source_table": "t", "source_id": "1"}]}')$$,
  '22023', null, 'a parent that is not listed is refused');
select throws_ok(
  $$select ledger.record_run('{"run": {"pipeline": "content", "workflow": "x", "external_id": "v2", "status": "succeeded"},
     "items": [{"ref": "l", "kind": "story", "source_table": "xsolla_ai_content_inbox", "source_id": "812"}]}')$$,
  '22023', null, 'an existing item sent with another kind is refused');
select throws_ok(
  $$select ledger.record_run('{"run": {"pipeline": "content", "workflow": "x", "external_id": "v3", "status": "succeeded"},
     "items": [{"ref": "l", "kind": "lead", "source_table": "xsolla_ai_content_inbox", "source_id": "812"},
               {"ref": "p", "kind": "post", "parent": "l", "source_table": "t", "source_id": "2"}]}')$$,
  '22023', null, 'a post directly under a lead is refused');
select throws_ok(
  $$select ledger.record_run('{"run": {"pipeline": "content", "workflow": "x", "external_id": "v4", "status": "succeeded"},
     "steps": [{"idempotency_key": "v4:a", "provider": "p", "purpose": "clean", "cost_usd": 0.1}]}')$$,
  '22023', null, 'a cost without cost_source is refused');
select throws_ok(
  $$select ledger.record_run('{"run": {"pipeline": "content", "workflow": "content_provider", "external_id": "cp-812",
       "status": "succeeded", "item": "l"},
     "items": [{"ref": "l", "kind": "lead", "source_table": "xsolla_ai_content_inbox", "source_id": "999"}]}')$$,
  '22023', null, 'moving a run to another item is refused');
select is((select count(*)::integer from ledger.runs where workflow = 'x'), 0, 'refused payloads wrote nothing');
select is(
  (select count(*)::integer from ledger.items where source_table = 't' or source_id = '999'), 0,
  'refused payloads created no items');

select * from finish();
rollback;
