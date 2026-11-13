-- The plan's worked example, reproduced exactly; shares change when a later Publisher run adds a
-- post; the video example; and recompute_costs() reproducing the incrementally kept fields.
begin;
create extension if not exists pgtap with schema extensions;
\ir fixtures/worked_example.sql
select plan(36);

-- Lead #812: scrape 0.0030 + clean 0.0021 + community 0.0004 + embedding 0.0001 + image analysis 0.0034
select is(pg_temp.send('cp_812') ->> 'steps_inserted', '5', 'Content Provider run recorded');
select is((pg_temp.item('812')).own_cost_usd, 0.0090::numeric, 'lead own = 0.0090');
select is((pg_temp.item('812')).upstream_share_usd, null::numeric, 'lead has no upstream share');
select is((pg_temp.item('812')).total_cost_usd, 0.0090::numeric, 'lead total = 0.0090');

-- First Publisher run: image for the story, three posts
select is(pg_temp.send('pub_1') ->> 'steps_inserted', '4', 'first Publisher run recorded');
select is((pg_temp.item('455')).own_cost_usd, 0.0400::numeric, 'story own = 0.0400');
select is((pg_temp.item('455')).upstream_share_usd, 0.0090::numeric, 'story share = 0.0090 / 1 story');
select is((pg_temp.item('455')).total_cost_usd, 0.0490::numeric, 'story total = 0.0490');
select is((pg_temp.item('7001')).upstream_share_usd, 0.0163333333::numeric, 'with three posts, each share = 0.0490 / 3');
select is((pg_temp.item('7001')).total_cost_usd, 0.0175333333::numeric, 'RU post total with three posts');

-- A later Publisher run adds the fourth post: every share changes
select is(pg_temp.send('pub_2') ->> 'steps_inserted', '1', 'second Publisher run recorded');
select is((pg_temp.item('7001')).upstream_share_usd, 0.01225::numeric, 'with four posts, each share = 0.0490 / 4');
select is((pg_temp.item('7001')).own_cost_usd, 0.0012::numeric, 'Telegram RU own = 0.0012');
select is((pg_temp.item('7001')).total_cost_usd, 0.01345::numeric, 'Telegram RU total = 0.01345');
select is((pg_temp.item('7002')).total_cost_usd, 0.01335::numeric, 'Telegram EN total = 0.01335');
select is((pg_temp.item('7003')).total_cost_usd, 0.01325::numeric, 'Discord total = 0.01325');
select is((pg_temp.item('7004')).total_cost_usd, 0.01315::numeric, 'X total = 0.01315');
select is((pg_temp.item('455')).total_cost_usd, 0.0490::numeric, 'story total is unchanged by the new post');

-- The split moves cost down to the posts and never creates or loses money
select is((pg_temp.run('cp-812')).total_cost_usd, 0.0090::numeric, 'Content Provider run total = 0.0090');
select is(
  (pg_temp.run('pub-1')).total_cost_usd + (pg_temp.run('pub-2')).total_cost_usd,
  0.0442::numeric, 'Publisher runs together = 0.0442');
select is(
  (select sum(total_cost_usd) from ledger.items where kind = 'post'),
  0.0532::numeric, 'the four posts add up to 0.0532');
select is(
  (select sum(total_cost_usd) from ledger.runs where external_id in ('cp-812', 'pub-1', 'pub-2')),
  (select sum(total_cost_usd) from ledger.items where kind = 'post'),
  'posts total = runs total');
select is(
  (select sum(cost_usd) from ledger.steps),
  (select sum(total_cost_usd) from ledger.runs),
  'sum of steps = sum of runs');

-- A rejected lead keeps its cost
select is(pg_temp.send('cp_813') ->> 'steps_inserted', '3', 'rejected lead recorded');
select is((pg_temp.item('813')).total_cost_usd, 0.0052::numeric, 'rejected lead total = 0.0052');
select is((pg_temp.run('cp-813')).outcome, 'duplicate', 'rejection reason kept on the run');

-- A video: 6 x 0.08 + 5 x 0.42 + one billed clip that failed and was redone; TTS has no price
select is(pg_temp.send('vid_1') ->> 'steps_inserted', '13', 'video run recorded');
select is((pg_temp.run('20261113-101500-4242')).total_cost_usd, 3.00::numeric, 'video run total = 3.00');
select is((pg_temp.run('20261113-101500-4242')).failed_attempts_cost_usd, 0.42::numeric, 'failed attempts = 0.42');
select is((pg_temp.run('20261113-101500-4242')).unpriced_calls, 1, 'one call not priced (TTS)');
select is((pg_temp.item('20261113-101500-4242')).total_cost_usd, 3.00::numeric, 'cost per video = 3.00 (a lower bound)');
select is((pg_temp.item('20261113-101500-4242')).unpriced_calls, 1, 'the video shows 1 call not priced');

-- recompute_costs() agrees with the incrementally kept fields
select is(ledger.recompute_costs(), '{"runs_changed": 0, "items_changed": 0}'::jsonb,
  'recompute_costs changes nothing on a consistent ledger');

create temp table kept as select * from cost_fields;
update ledger.items set own_cost_usd = null, upstream_share_usd = null, total_cost_usd = null, unpriced_calls = null;
update ledger.runs set total_cost_usd = null, failed_attempts_cost_usd = null, unpriced_calls = null;
select is(ledger.recompute_costs(), '{"runs_changed": 5, "items_changed": 8}'::jsonb,
  'after wiping every cost field, recompute_costs rewrites all 5 runs and 8 items');
select is(
  (select count(*)::integer from (
     (select * from kept except select * from cost_fields)
     union all
     (select * from cost_fields except select * from kept)) d),
  0, 'rebuilt cost fields equal the incrementally kept ones');
select is(ledger.recompute_costs(), '{"runs_changed": 0, "items_changed": 0}'::jsonb,
  'a second recompute changes nothing');

select * from finish();
rollback;
