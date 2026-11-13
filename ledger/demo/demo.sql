-- Ledger demo: sends the plan's worked example through the real ledger.record_run() and prints
-- what the ledger keeps after each step. Run with ledger/demo/run.sh, never against a real database.
\set QUIET on
\pset null '—'
\pset footer off
\pset border 1
\ir ../tests/fixtures/worked_example.sql

create temp view demo_items as
select case kind
         when 'lead'  then 'lead #' || source_id
         when 'story' then 'story #' || source_id
         when 'post'  then 'post ' || coalesce(channel_type || ' ' || upper(language), source_id)
         else kind || ' ' || source_id
       end as item,
       own_cost_usd::numeric(10, 5) as "own $",
       upstream_share_usd::numeric(10, 5) as "share $",
       total_cost_usd::numeric(10, 5) as "total $",
       unpriced_calls as "not priced",
       id
  from ledger.items;

create function pg_temp.said(r jsonb) returns text language sql as $$
  select format('-> record_run: run %s, %s paid call%s recorded, %s skipped as already recorded',
                r ->> 'run_id', r ->> 'steps_inserted',
                case when r ->> 'steps_inserted' = '1' then '' else 's' end,
                r ->> 'steps_skipped') $$;

\echo
\echo '1) Content Provider processes one PALWORLD Reddit link (lead #812) into story #455'
\echo '   5 paid calls: scrape, clean, community, embedding, image check'
select pg_temp.said(pg_temp.send('cp_812')) as said \gset
\echo '  ' :said
select item, "own $", "share $", "total $" from demo_items order by id;
\if :{?pause}
\prompt '   [Enter] ' _
\endif

\echo
\echo '2) Publisher: one image for the story, then three posts (Telegram RU, Telegram EN, Discord)'
select pg_temp.said(pg_temp.send('pub_1')) as said \gset
\echo '  ' :said
select item, "own $", "share $", "total $" from demo_items order by id;
\echo '   Each post takes a third of the story''s $0.049.'
\if :{?pause}
\prompt '   [Enter] ' _
\endif

\echo
\echo '3) A later Publisher run adds a post for X: every post''s share is recalculated'
select pg_temp.said(pg_temp.send('pub_2')) as said \gset
\echo '  ' :said
select item, "own $", "share $", "total $" from demo_items where item like 'post%' order by id;
select (select sum(total_cost_usd) from ledger.items where kind = 'post')::numeric(10, 5) as "4 posts together $",
       (select sum(total_cost_usd) from ledger.runs)::numeric(10, 5) as "what the runs spent $";
\if :{?pause}
\prompt '   [Enter] ' _
\endif

\echo
\echo '4) The collector sends the same run again'
select pg_temp.said(pg_temp.send('pub_2')) as said \gset
\echo '  ' :said
\echo '   Nothing is counted twice.'
\if :{?pause}
\prompt '   [Enter] ' _
\endif

\echo
\echo '5) A duplicate lead is rejected, and a video run has a failed clip and an unpriced voice-over'
select pg_temp.said(pg_temp.send('cp_813')) as said \gset
\echo '  ' :said
select pg_temp.said(pg_temp.send('vid_1')) as said \gset
\echo '  ' :said
select workflow, status, outcome,
       total_cost_usd::numeric(10, 5) as "total $",
       failed_attempts_cost_usd::numeric(10, 5) as "wasted on retries $",
       unpriced_calls as "not priced"
  from ledger.runs order by id;
\if :{?pause}
\prompt '   [Enter] ' _
\endif

-- Stand-in for the pipeline's post table, so the views can read live post status.
create table public.xsolla_ai_posted_content_base (
  id bigint primary key, status text, created_at timestamptz default now(), status_updated_at timestamptz);
insert into public.xsolla_ai_posted_content_base (id, status) values
  (7001, 'posted'), (7002, 'posted'), (7003, 'approved'), (7004, 'decline');
select ledger.link_post_status() as " " \g /dev/null

\echo
\echo '6) Waste by reason (the moderator declined the X post)'
select pipeline, reason, waste_usd::numeric(10, 5) as "wasted $" from ledger.v_waste_day order by pipeline, reason;
\echo
\echo '7) What the Statistics tab reads: AI Content, today, per game'
select game, posts_generated as generated, posts_approved as approved, posts_rejected as rejected,
       posts_published as published, leads_rejected as "leads rejected",
       spend_usd::numeric(10, 5) as "spend $", waste_usd::numeric(10, 5) as "waste $",
       (spend_usd / nullif(posts_published, 0))::numeric(10, 5) as "per published post $"
  from ledger.v_content_stats_day;
\echo
