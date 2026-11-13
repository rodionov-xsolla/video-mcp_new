-- V003: read views. `ledger_reader` may select these and nothing else.
--
-- Days are UTC dates. Every spend column holds the known part; the matching `unpriced_calls`
-- says how many calls behind it have no price ("≥ $X, N not priced").

-- Live post status, read from the pipeline's own table so it never goes stale.
-- Created by a function because that table exists in the pipeline database but not in a fresh
-- local one: there the view is empty, with the same columns. Call ledger.link_post_status()
-- again if the table appears later.
create or replace function ledger.link_post_status()
returns text
language plpgsql
security definer
set search_path = ''
as $$
begin
  if to_regclass('public.xsolla_ai_posted_content_base') is not null then
    execute $view$
      create or replace view ledger.v_post_live_status as
      select p.id::text as source_id,
             p.status::text as status,
             case
               when p.status = 'posted' then 'published'
               when p.status in ('approved', 'posting') then 'approved'
               when p.status = 'decline' then 'declined'
               when p.status = 'error' then 'error'
               when p.status in ('wait moderation', 'on moderation', 'translation') then 'waiting'
               else 'other'
             end as stage,
             coalesce(p.status_updated_at, p.created_at)::timestamptz as status_at
        from public.xsolla_ai_posted_content_base p
    $view$;
    return 'linked';
  end if;

  execute $view$
    create or replace view ledger.v_post_live_status as
    select null::text as source_id,
           null::text as status,
           null::text as stage,
           null::timestamptz as status_at
     where false
  $view$;
  return 'empty';
end
$$;

revoke all on function ledger.link_post_status() from public;
select ledger.link_post_status();

comment on view ledger.v_post_live_status is
  'Live status of each post from xsolla_ai_posted_content_base. stage: waiting, approved, published, declined, error, other.';

-- Plain projections for the read API.
create view ledger.v_items as
select i.*,
       (select count(*) from ledger.items k where k.parent_id = i.id) as children,
       p.status as live_status,
       p.stage as live_stage,
       p.status_at as live_status_at,
       lr.id as last_run_id,
       lr.status as last_run_status,
       lr.outcome as last_run_outcome
  from ledger.items i
  left join ledger.v_post_live_status p
         on i.kind = 'post'
        and i.source_table = 'xsolla_ai_posted_content_base'
        and p.source_id = i.source_id
  left join lateral (
         select r.id, r.status, r.outcome
           from ledger.runs r
          where r.item_id = i.id
          order by coalesce(r.finished_at, r.started_at, r.recorded_at) desc, r.id desc
          limit 1
       ) lr on true;

create view ledger.v_runs as
select r.*,
       i.kind as item_kind,
       i.source_table as item_source_table,
       i.source_id as item_source_id,
       i.game,
       i.format
  from ledger.runs r
  left join ledger.items i on i.id = r.item_id;

create view ledger.v_steps as
select s.*,
       r.pipeline,
       r.workflow,
       r.external_id,
       r.status as run_status,
       i.kind as item_kind,
       i.game,
       i.format
  from ledger.steps s
  join ledger.runs r on r.id = s.run_id
  left join ledger.items i on i.id = s.item_id;

-- Spend, by the finest grain the panel needs. Group it further for spend by purpose, top spenders
-- (node, model, purpose) and trends.
create view ledger.v_spend_day as
select (s.created_at at time zone 'UTC')::date as day,
       r.pipeline,
       r.workflow,
       s.node,
       s.provider,
       s.model,
       s.purpose,
       i.game,
       i.format,
       coalesce(sum(s.cost_usd), 0) as spend_usd,
       count(*) as calls,
       count(*) filter (where s.cost_usd is null) as unpriced_calls,
       count(*) filter (where not s.ok) as failed_calls
  from ledger.steps s
  join ledger.runs r on r.id = s.run_id
  left join ledger.items i on i.id = s.item_id
 group by 1, 2, 3, 4, 5, 6, 7, 8, 9;

create view ledger.v_cost_by_game_day as
select day, pipeline, game,
       sum(spend_usd) as spend_usd, sum(calls) as calls, sum(unpriced_calls) as unpriced_calls
  from ledger.v_spend_day
 group by day, pipeline, game;

create view ledger.v_cost_by_format_day as
select day, pipeline, format,
       sum(spend_usd) as spend_usd, sum(calls) as calls, sum(unpriced_calls) as unpriced_calls
  from ledger.v_spend_day
 group by day, pipeline, format;

-- Each item's cost without the money that bought nothing (failed or superseded calls, and calls
-- inside failed or aborted runs), rolled down the tree the same way as total_cost_usd. Helper for
-- v_waste, so that no cent is counted under two waste reasons.
create view ledger.v_item_clean_cost as
with recursive own as (
  select i.id,
         i.parent_id,
         coalesce(sum(s.cost_usd) filter (
           where s.ok and not s.superseded and r.status not in ('failed', 'aborted')), 0) as clean_own,
         (select count(*) from ledger.items k where k.parent_id = i.id)::integer as n_children
    from ledger.items i
    left join ledger.steps s on s.item_id = i.id
    left join ledger.runs r on r.id = s.run_id
   group by i.id, i.parent_id
),
tree as (
  select o.id, o.clean_own, o.clean_own::numeric as clean_total, o.n_children
    from own o
   where o.parent_id is null
  union all
  select o.id, o.clean_own, round(o.clean_own + t.clean_total / t.n_children, 10), o.n_children
    from tree t
    join own o on o.parent_id = t.id
)
select id as item_id, clean_own as clean_own_usd, clean_total as clean_total_usd
  from tree;

-- Waste: one row per piece of money that bought nothing, each counted under exactly one reason.
--   failed_call       a call that failed, or was redone by a later attempt
--   failed_run        a successful call inside a run that failed or was aborted
--   rejected:<why>    a lead, story or video that was rejected and has no children
--                     (its clean cost, including its share of the parent)
--   declined          a post a moderator declined (its clean cost, including its share)
--   post_error        a post whose live status is error
create view ledger.v_waste as
select r.pipeline,
       i.game,
       i.format,
       (s.created_at at time zone 'UTC')::date as day,
       'failed_call'::text as reason,
       coalesce(s.cost_usd, 0) as cost_usd,
       (s.cost_usd is null)::integer as unpriced_calls,
       s.item_id,
       s.run_id,
       s.id as step_id
  from ledger.steps s
  join ledger.runs r on r.id = s.run_id
  left join ledger.items i on i.id = s.item_id
 where not s.ok or s.superseded
union all
select r.pipeline, i.game, i.format, (s.created_at at time zone 'UTC')::date,
       'failed_run', coalesce(s.cost_usd, 0), (s.cost_usd is null)::integer,
       s.item_id, s.run_id, s.id
  from ledger.steps s
  join ledger.runs r on r.id = s.run_id
  left join ledger.items i on i.id = s.item_id
 where s.ok and not s.superseded and r.status in ('failed', 'aborted')
union all
select i.pipeline, i.game, i.format, (i.created_at at time zone 'UTC')::date,
       'rejected:' || coalesce(lr.outcome, 'unknown'), c.clean_total_usd, coalesce(i.unpriced_calls, 0),
       i.id, lr.id, null::bigint
  from ledger.items i
  join ledger.v_item_clean_cost c on c.item_id = i.id
  join lateral (
         select r.id, r.status, r.outcome
           from ledger.runs r
          where r.item_id = i.id
          order by coalesce(r.finished_at, r.started_at, r.recorded_at) desc, r.id desc
          limit 1
       ) lr on true
 where i.kind in ('lead', 'story', 'video')
   and lr.status = 'rejected'
   and not exists (select from ledger.items k where k.parent_id = i.id)
union all
select i.pipeline, i.game, i.format, (i.created_at at time zone 'UTC')::date,
       case p.stage when 'declined' then 'declined' else 'post_error' end,
       c.clean_total_usd, coalesce(i.unpriced_calls, 0),
       i.id, null::bigint, null::bigint
  from ledger.items i
  join ledger.v_post_live_status p
    on i.source_table = 'xsolla_ai_posted_content_base' and p.source_id = i.source_id
  join ledger.v_item_clean_cost c on c.item_id = i.id
 where i.kind = 'post'
   and p.stage in ('declined', 'error');

create view ledger.v_waste_day as
select day, pipeline, game, reason,
       sum(cost_usd) as waste_usd,
       sum(unpriced_calls) as unpriced_calls,
       count(distinct item_id) as items
  from ledger.v_waste
 group by day, pipeline, game, reason;

-- Statistics tab, XPN AI Content: one row per day and game. Cost per published post over a period
-- is sum(spend_usd) / sum(posts_published); compute it after summing, never per day.
create view ledger.v_content_stats_day as
with posts as (
  select (i.created_at at time zone 'UTC')::date as day,
         i.game,
         count(*) as posts_generated,
         count(*) filter (where p.stage in ('approved', 'published')) as posts_approved,
         count(*) filter (where p.stage = 'declined') as posts_rejected,
         count(*) filter (where p.stage = 'published') as posts_published
    from ledger.items i
    left join ledger.v_post_live_status p
           on i.source_table = 'xsolla_ai_posted_content_base' and p.source_id = i.source_id
   where i.kind = 'post' and i.pipeline = 'content'
   group by 1, 2
),
leads as (
  select day, game, count(distinct item_id) as leads_rejected
    from ledger.v_waste
   where pipeline = 'content' and reason like 'rejected:%'
   group by 1, 2
),
spend as (
  select day, game, sum(spend_usd) as spend_usd, sum(unpriced_calls) as unpriced_calls
    from ledger.v_spend_day
   where pipeline = 'content'
   group by 1, 2
),
waste as (
  select day, game, sum(cost_usd) as waste_usd
    from ledger.v_waste
   where pipeline = 'content'
   group by 1, 2
),
days as (
  select day, game from posts
  union select day, game from leads
  union select day, game from spend
  union select day, game from waste
)
select d.day,
       d.game,
       coalesce(p.posts_generated, 0) as posts_generated,
       coalesce(p.posts_approved, 0) as posts_approved,
       coalesce(p.posts_rejected, 0) as posts_rejected,
       coalesce(p.posts_published, 0) as posts_published,
       coalesce(l.leads_rejected, 0) as leads_rejected,
       coalesce(s.spend_usd, 0) as spend_usd,
       coalesce(s.unpriced_calls, 0) as unpriced_calls,
       coalesce(w.waste_usd, 0) as waste_usd
  from days d
  left join posts p on p.day = d.day and p.game is not distinct from d.game
  left join leads l on l.day = d.day and l.game is not distinct from d.game
  left join spend s on s.day = d.day and s.game is not distinct from d.game
  left join waste w on w.day = d.day and w.game is not distinct from d.game;

-- Statistics tab, XPN Video Generation: one row per day, format and game. An approved video is a
-- run with outcome approved_final. Publication per platform is not in the ledger.
create view ledger.v_video_stats_day as
select (coalesce(r.started_at, r.recorded_at) at time zone 'UTC')::date as day,
       i.format,
       i.game,
       count(*) as runs,
       count(*) filter (where r.outcome = 'approved_final') as approved_videos,
       count(*) filter (where r.status in ('failed', 'aborted')) as failed_or_aborted_runs,
       coalesce(sum(r.total_cost_usd), 0) as spend_usd,
       coalesce(sum(r.failed_attempts_cost_usd), 0) as failed_attempts_cost_usd,
       coalesce(sum(r.unpriced_calls), 0) as unpriced_calls,
       count(*) filter (where r.total_cost_usd is null) as runs_not_recorded
  from ledger.runs r
  left join ledger.items i on i.id = r.item_id
 where r.pipeline = 'video'
 group by 1, 2, 3;

-- Posts and videos above the 95th-percentile total cost of their pipeline, kind and format.
create view ledger.v_item_outliers as
with costs as (
  select i.id, i.kind, i.pipeline, i.format, i.game, i.title, i.total_cost_usd, i.unpriced_calls, i.created_at
    from ledger.items i
   where i.kind in ('post', 'video') and i.total_cost_usd is not null
),
p95 as (
  select kind, pipeline, format,
         percentile_cont(0.95) within group (order by total_cost_usd) as p95_usd,
         count(*) as group_size
    from costs
   group by kind, pipeline, format
)
select c.*,
       p.p95_usd,
       p.group_size,
       coalesce(
         (select r.id from ledger.runs r where r.item_id = c.id order by r.id desc limit 1),
         (select s.run_id from ledger.steps s where s.item_id = c.id order by s.id limit 1)
       ) as run_id
  from costs c
  join p95 p
    on p.kind = c.kind and p.pipeline = c.pipeline and p.format is not distinct from c.format
 where c.total_cost_usd > p.p95_usd;

-- What one story costs as it fans out to channels and languages.
create view ledger.v_fanout as
select st.id as story_id,
       st.game,
       st.title,
       st.created_at,
       count(p.id) as posts,
       count(distinct p.channel_id) as channels,
       count(distinct p.language) as languages,
       st.total_cost_usd as story_total_usd,
       coalesce(sum(p.own_cost_usd), 0) as posts_own_usd,
       st.total_cost_usd + coalesce(sum(p.own_cost_usd), 0) as tree_total_usd
  from ledger.items st
  left join ledger.items p on p.parent_id = st.id and p.kind = 'post'
 where st.kind = 'story'
 group by st.id;

-- Health for System Status: per workflow (runs) and per provider (calls).
create view ledger.v_run_health_24h as
with r as (
  select runs.*, coalesce(finished_at, started_at, recorded_at) as at
    from ledger.runs
)
select r.pipeline,
       r.workflow,
       count(*) filter (where r.at >= now() - interval '24 hours') as runs_24h,
       count(*) filter (where r.at >= now() - interval '24 hours' and r.status = 'failed') as failed_runs_24h,
       max(r.at) as last_run_at,
       max(r.at) filter (where r.status in ('succeeded', 'rejected')) as last_success_at,
       max(r.at) filter (where r.status = 'failed') as last_failure_at,
       (select f.error_message
          from ledger.runs f
         where f.workflow = r.workflow and f.status = 'failed'
         order by coalesce(f.finished_at, f.started_at, f.recorded_at) desc, f.id desc
         limit 1) as last_error_message
  from r
 group by r.pipeline, r.workflow;

create view ledger.v_provider_health_24h as
select s.provider,
       count(*) filter (where s.created_at >= now() - interval '24 hours') as calls_24h,
       count(*) filter (where s.created_at >= now() - interval '24 hours' and not s.ok) as failed_calls_24h,
       max(s.created_at) filter (where s.ok) as last_ok_at,
       max(s.created_at) filter (where not s.ok) as last_error_at,
       (select e.error_message
          from ledger.steps e
         where e.provider = s.provider and not e.ok
         order by e.created_at desc, e.id desc
         limit 1) as last_error_message
  from ledger.steps s
 group by s.provider;

-- The reader gets every view in the schema and nothing else.
do $$
declare
  v record;
begin
  for v in select viewname from pg_views where schemaname = 'ledger' loop
    execute format('grant select on ledger.%I to ledger_reader', v.viewname);
  end loop;
end
$$;
