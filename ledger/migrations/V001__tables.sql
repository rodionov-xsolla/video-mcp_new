-- V001: the ledger schema, its three tables, two roles and row-level security.
--
-- Additive only: creates schema `ledger` and the NOLOGIN roles `ledger_writer` and
-- `ledger_reader`. Touches no existing table.
--
-- Cost rule for every cost column: NULL means "we don't know", never zero. A total holds the
-- known part, and `unpriced_calls` says how many calls behind it have no price.

create schema if not exists ledger;
comment on schema ledger is
  'Cost ledger: one row per item, run and paid call. Written only through ledger.record_run().';

do $$
begin
  if not exists (select from pg_roles where rolname = 'ledger_writer') then
    create role ledger_writer nologin;
  end if;
  if not exists (select from pg_roles where rolname = 'ledger_reader') then
    create role ledger_reader nologin;
  end if;
end
$$;

comment on role ledger_writer is 'May call ledger.record_run(). Login roles (e.g. ledger_n8n) are members.';
comment on role ledger_reader is 'May read the ledger views, nothing else.';

revoke all on schema ledger from public;
grant usage on schema ledger to ledger_writer, ledger_reader, service_role;

-- items: one row per lead, story, post or video.
create table ledger.items (
  id                 bigint generated always as identity primary key,
  kind               text not null check (kind in ('lead', 'story', 'post', 'video')),
  pipeline           text not null check (pipeline in ('content', 'video', 'influencer')),
  parent_id          bigint references ledger.items (id),
  source_table       text not null,
  source_id          text not null,
  game               text,
  format             text,
  channel_id         text,
  channel_type       text,
  language           text,
  title              text,
  created_at         timestamptz not null default now(),
  own_cost_usd       numeric(20, 10) check (own_cost_usd >= 0),
  upstream_share_usd numeric(20, 10) check (upstream_share_usd >= 0),
  total_cost_usd     numeric(20, 10) check (total_cost_usd >= 0),
  unpriced_calls     integer check (unpriced_calls >= 0),
  unique (source_table, source_id),
  check (parent_id is null or parent_id <> id)
);

create index items_parent_id_idx on ledger.items (parent_id);
create index items_kind_created_at_idx on ledger.items (kind, created_at);

comment on table ledger.items is 'One row per lead, story, post or video. Answers "what did this item cost, all in?"';
comment on column ledger.items.source_id is 'The pipeline''s own id, as text. Unique together with source_table.';
comment on column ledger.items.own_cost_usd is
  'Known cost of the steps whose item_id is this item. NULL when no run or step was recorded for it.';
comment on column ledger.items.upstream_share_usd is
  'Equal share of the parent''s total: parent total / number of the parent''s children. '
  'NULL for items without a parent, and when the parent''s cost is not recorded.';
comment on column ledger.items.total_cost_usd is
  'own + upstream share. Cost per post or per video. Never add it up across kinds.';
comment on column ledger.items.unpriced_calls is
  'Unpriced calls behind total_cost_usd: this item''s own plus its parent''s. Above 0 means the total is a lower bound.';

-- runs: one row per workflow execution or video run.
create table ledger.runs (
  id                       bigint generated always as identity primary key,
  pipeline                 text not null check (pipeline in ('content', 'video', 'influencer')),
  workflow                 text not null check (workflow ~ '^[a-z][a-z0-9_]*$'),
  external_id              text not null,
  workflow_version         text,
  item_id                  bigint references ledger.items (id),
  status                   text not null
                             check (status in ('running', 'succeeded', 'failed', 'rejected', 'aborted')),
  outcome                  text,
  started_at               timestamptz,
  finished_at              timestamptz,
  error_message            text,
  source                   text not null default 'collector'
                             check (source in ('collector', 'inline', 'backfill', 'legacy_copy')),
  cost_recorded            boolean not null default true,
  total_cost_usd           numeric(20, 10) check (total_cost_usd >= 0),
  failed_attempts_cost_usd numeric(20, 10) check (failed_attempts_cost_usd >= 0),
  unpriced_calls           integer check (unpriced_calls >= 0),
  recorded_at              timestamptz not null default now(),
  updated_at               timestamptz not null default now(),
  unique (workflow, external_id)
);

create index runs_item_id_idx on ledger.runs (item_id);
create index runs_started_at_idx on ledger.runs (started_at);

comment on table ledger.runs is 'One row per execution or video run. Answers "what did this one execution cost?"';
comment on column ledger.runs.external_id is 'The n8n execution id or the video RUN_ID. Unique together with workflow.';
comment on column ledger.runs.cost_recorded is
  'False when the run''s calls were not captured (e.g. legacy_copy). Its cost fields are then NULL unless it has steps.';
comment on column ledger.runs.total_cost_usd is 'Known cost of all the run''s steps.';
comment on column ledger.runs.failed_attempts_cost_usd is
  'Part of the total spent on calls that failed or that a retry superseded. Already included in the total.';

-- steps: one row per paid call.
create table ledger.steps (
  id              bigint generated always as identity primary key,
  run_id          bigint not null references ledger.runs (id),
  item_id         bigint references ledger.items (id),
  idempotency_key text not null unique,
  node            text,
  provider        text not null,
  model           text,
  purpose         text not null check (purpose ~ '^[a-z][a-z0-9_]*$'),
  ok              boolean not null default true,
  error_message   text,
  attempt         integer not null default 1 check (attempt >= 1),
  is_retry        boolean not null default false,
  superseded      boolean not null default false,
  cost_usd        numeric(20, 10) check (cost_usd >= 0),
  cost_source     text not null check (cost_source in ('reported', 'computed', 'estimated', 'unknown')),
  unit            text check (unit ~ '^[a-z][a-z0-9_]*$'),
  units_in        numeric check (units_in >= 0),
  units_out       numeric check (units_out >= 0),
  units           numeric check (units >= 0),
  unit_price_usd  numeric(20, 10) check (unit_price_usd >= 0),
  created_at      timestamptz not null default now(),
  check ((cost_usd is null) = (cost_source = 'unknown')),
  check (cost_source <> 'computed' or (units is not null and unit_price_usd is not null))
);

create index steps_run_id_idx on ledger.steps (run_id);
create index steps_item_id_idx on ledger.steps (item_id);
create index steps_created_at_idx on ledger.steps (created_at);

comment on table ledger.steps is 'One row per paid call. The evidence behind every cost field.';
comment on column ledger.steps.idempotency_key is
  'Stops a re-send from counting twice, e.g. n8n:<exec>:<node>:<runIndex>:<itemIndex> or video:<job_id>:<attempt>.';
comment on column ledger.steps.cost_usd is 'What this call cost. NULL when unknown, never 0 for unknown.';
comment on column ledger.steps.unit_price_usd is
  'Price per unit used for a computed cost, kept so later price changes never rewrite old costs.';
comment on column ledger.steps.created_at is 'When the call happened (sent by the collector), else when it was recorded.';

-- Row-level security on, with no policies: nobody reads the tables directly except their owner.
-- Writes go through ledger.record_run() (V002); reads go through the views (V003).
alter table ledger.items enable row level security;
alter table ledger.runs enable row level security;
alter table ledger.steps enable row level security;

revoke all on all tables in schema ledger from public, anon, authenticated, service_role;
