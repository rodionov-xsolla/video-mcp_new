-- Views: live post status, content and video statistics, waste without double counting, spend,
-- fan-out, outliers and health. Uses a stand-in for xsolla_ai_posted_content_base, created and
-- dropped inside this test's transaction.
begin;
create extension if not exists pgtap with schema extensions;
\ir fixtures/worked_example.sql
select plan(26);

do $$ begin perform pg_temp.send(name) from fx order by name; end $$;

-- Stand-in for the pipeline's post table, with the statuses the workflows write
create table public.xsolla_ai_posted_content_base (
  id bigint primary key,
  status text,
  created_at timestamptz default now(),
  status_updated_at timestamptz
);
insert into public.xsolla_ai_posted_content_base (id, status) values
  (7001, 'posted'), (7002, 'posted'), (7003, 'approved'), (7004, 'decline');

select is(ledger.link_post_status(), 'linked', 'live status view links to the post table when it exists');
select is((select live_stage from ledger.v_items where source_id = '7004'), 'declined', '"decline" maps to stage declined');
select is((select live_stage from ledger.v_items where source_id = '7001'), 'published', '"posted" maps to stage published');
select is((select children::integer from ledger.v_items where source_id = '455'), 4, 'v_items counts children');
select is((select last_run_outcome from ledger.v_items where source_id = '813'), 'duplicate', 'v_items shows the last run outcome');

-- Content statistics for today (the fixture's calls are stamped with now())
create temp view today as
select * from ledger.v_content_stats_day
 where day = (now() at time zone 'UTC')::date and game = 'PALWORLD';
select is((select posts_generated::integer from today), 4, 'posts generated');
select is((select posts_approved::integer from today), 3, 'posts approved (approved or published)');
select is((select posts_rejected::integer from today), 1, 'posts rejected (declined)');
select is((select posts_published::integer from today), 2, 'posts published');
select is((select leads_rejected::integer from today), 1, 'leads rejected');
select is((select spend_usd from today), 0.0584::numeric, 'content spend = 0.0532 + 0.0052');
select is((select waste_usd from today), 0.01835::numeric, 'content waste = rejected lead 0.0052 + declined X post 0.01315');

-- Waste: each cent under one reason only
select is((select cost_usd from ledger.v_waste where reason = 'rejected:duplicate'), 0.0052::numeric, 'rejected:duplicate = 0.0052');
select is((select cost_usd from ledger.v_waste where reason = 'declined'), 0.01315::numeric, 'declined post = its full cost 0.01315');
select is(
  (select sum(cost_usd) from ledger.v_waste where pipeline = 'video' and reason = 'failed_call'),
  0.42::numeric, 'video failed attempt = 0.42');
select ok(
  (select sum(cost_usd) from ledger.v_waste) <= (select sum(cost_usd) from ledger.steps),
  'total waste never exceeds total spend');
select is(
  (select count(*)::integer from (select step_id from ledger.v_waste where step_id is not null
                                  group by step_id having count(*) > 1) d),
  0, 'no call is counted under two waste reasons');

-- Spend
select is(
  (select sum(spend_usd) from ledger.v_spend_day where purpose = 'localize'),
  0.0042::numeric, 'spend on localization = 0.0042');
select is(
  (select sum(unpriced_calls)::integer from ledger.v_spend_day where pipeline = 'video'),
  1, 'unpriced calls carried into spend');
select is(
  (select sum(spend_usd) from ledger.v_cost_by_game_day where game = 'PALWORLD'),
  (select sum(cost_usd) from ledger.steps), 'spend by game adds up to all steps');

-- Video statistics
select is((select approved_videos::integer from ledger.v_video_stats_day), 1, 'one approved video');
select is((select spend_usd from ledger.v_video_stats_day), 3.00::numeric, 'video spend = 3.00');

-- Fan-out
select is((select posts::integer from ledger.v_fanout where story_id = (pg_temp.item('455')).id), 4, 'story fans out to four posts');
select is((select tree_total_usd from ledger.v_fanout where story_id = (pg_temp.item('455')).id), 0.0532::numeric, 'whole tree costs 0.0532');

-- Health (move the fixture's fixed run times to now, so the 24-hour window holds on any day)
update ledger.runs set started_at = now(), finished_at = now();
select is((select runs_24h::integer from ledger.v_run_health_24h where workflow = 'publisher'), 2, 'publisher ran twice in 24 h');
select is((select failed_calls_24h::integer from ledger.v_provider_health_24h where provider = 'fal'), 1, 'one failed fal call in 24 h');

select * from finish();
rollback;
