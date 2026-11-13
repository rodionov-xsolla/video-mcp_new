-- V002: the write API.
--
--   ledger.record_run(payload jsonb)   the only way in; idempotent; one transaction
--   ledger.recompute_costs()           rebuilds every cost field from steps; returns what changed
--   public.ledger_record_run(jsonb)    thin wrapper so the service role can call it over PostgREST RPC
--
-- Payload contract: ledger/WRITE_API.md.

-- Recompute the cost fields of the given runs from their steps. Returns the number of runs changed.
create or replace function ledger._refresh_runs(p_run_ids bigint[])
returns integer
language plpgsql
set search_path = ''
as $$
declare
  v_n integer;
begin
  update ledger.runs r
     set total_cost_usd = c.total,
         failed_attempts_cost_usd = c.failed,
         unpriced_calls = c.unpriced
    from (
      select r2.id,
             case when count(s.id) = 0 and not r2.cost_recorded then null
                  else coalesce(sum(s.cost_usd), 0) end as total,
             case when count(s.id) = 0 and not r2.cost_recorded then null
                  else coalesce(sum(s.cost_usd) filter (where not s.ok or s.superseded), 0) end as failed,
             case when count(s.id) = 0 and not r2.cost_recorded then null
                  else (count(s.id) filter (where s.cost_usd is null))::integer end as unpriced
        from ledger.runs r2
        left join ledger.steps s on s.run_id = r2.id
       where r2.id = any (p_run_ids)
       group by r2.id, r2.cost_recorded
    ) c
   where r.id = c.id
     and (r.total_cost_usd, r.failed_attempts_cost_usd, r.unpriced_calls)
         is distinct from (c.total, c.failed, c.unpriced);
  get diagnostics v_n = row_count;
  return v_n;
end
$$;

-- Recompute own cost, upstream share, total and unpriced calls for every item in the trees that
-- contain the given items (root ancestor down to every descendant). A child's share is its parent's
-- total divided by the parent's number of children, so adding a post changes all its siblings.
-- Returns the number of items changed.
create or replace function ledger._refresh_items(p_item_ids bigint[])
returns integer
language plpgsql
set search_path = ''
as $$
declare
  v_roots bigint[];
  v_n integer;
begin
  if coalesce(cardinality(p_item_ids), 0) = 0 then
    return 0;
  end if;

  with recursive up as (
    select i.id, i.parent_id from ledger.items i where i.id = any (p_item_ids)
    union
    select p.id, p.parent_id from ledger.items p join up on p.id = up.parent_id
  )
  select array_agg(distinct up.id) into v_roots from up where up.parent_id is null;

  if v_roots is null then
    return 0;
  end if;

  -- Lock the trees in a fixed order, so two writers on the same tree queue instead of deadlocking.
  perform 1 from ledger.items where id = any (v_roots) order by id for update;

  with recursive tree as (
    select i.id from ledger.items i where i.id = any (v_roots)
    union all
    select c.id from ledger.items c join tree t on c.parent_id = t.id
  ),
  own as (
    select i.id,
           i.parent_id,
           case when exists (select from ledger.steps s where s.item_id = i.id)
                  or exists (select from ledger.runs r where r.item_id = i.id and r.cost_recorded)
                then (select coalesce(sum(s.cost_usd), 0) from ledger.steps s where s.item_id = i.id)
           end as own_cost,
           (select count(*) from ledger.steps s where s.item_id = i.id and s.cost_usd is null)::integer
             as own_unpriced,
           (select count(*) from ledger.items k where k.parent_id = i.id)::integer as n_children
      from ledger.items i
      join tree t on t.id = i.id
  ),
  rolled as (
    select o.id,
           o.own_cost,
           null::numeric as share,
           o.own_cost::numeric as total,
           case when o.own_cost is null then null else o.own_unpriced end as unpriced,
           o.n_children
      from own o
     where o.parent_id is null
    union all
    select o.id,
           o.own_cost,
           round(r.total / r.n_children, 10),
           case when o.own_cost is null and r.total is null then null
                else round(coalesce(o.own_cost, 0) + coalesce(round(r.total / r.n_children, 10), 0), 10)
           end,
           case when o.own_cost is null and r.total is null then null
                else (case when o.own_cost is null then 0 else o.own_unpriced end) + coalesce(r.unpriced, 0)
           end,
           o.n_children
      from rolled r
      join own o on o.parent_id = r.id
  )
  update ledger.items i
     set own_cost_usd = r.own_cost,
         upstream_share_usd = r.share,
         total_cost_usd = r.total,
         unpriced_calls = r.unpriced
    from rolled r
   where i.id = r.id
     and (i.own_cost_usd, i.upstream_share_usd, i.total_cost_usd, i.unpriced_calls)
         is distinct from (r.own_cost, r.share, r.total, r.unpriced);
  get diagnostics v_n = row_count;
  return v_n;
end
$$;

create or replace function ledger.record_run(payload jsonb)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_run         jsonb := payload -> 'run';
  v_items       jsonb := coalesce(payload -> 'items', '[]'::jsonb);
  v_steps       jsonb := coalesce(payload -> 'steps', '[]'::jsonb);
  v_item        jsonb;
  v_step        jsonb;
  v_refs        jsonb := '{}'::jsonb;
  v_ref         text;
  v_parent_id   bigint;
  v_parent_kind text;
  v_row         ledger.items;
  v_run_id      bigint;
  v_run_item    bigint;
  v_want_item   bigint;
  v_step_item   bigint;
  v_cost        numeric;
  v_source      text;
  v_touched     bigint[] := '{}';
  v_inserted    integer := 0;
  v_skipped     integer := 0;
  v_n           integer;
begin
  if jsonb_typeof(payload) is distinct from 'object' or jsonb_typeof(v_run) is distinct from 'object' then
    raise exception 'record_run: payload must be an object with a "run" object' using errcode = '22023';
  end if;
  if jsonb_typeof(v_items) <> 'array' or jsonb_typeof(v_steps) <> 'array' then
    raise exception 'record_run: "items" and "steps" must be arrays' using errcode = '22023';
  end if;

  -- 1. Items, in payload order. A parent must be listed before its children.
  for v_item in select value from jsonb_array_elements(v_items) loop
    v_ref := v_item ->> 'ref';
    if v_ref is null or v_item ->> 'kind' is null
       or v_item ->> 'source_table' is null or v_item ->> 'source_id' is null then
      raise exception 'record_run: every item needs ref, kind, source_table and source_id: %', v_item
        using errcode = '22023';
    end if;
    if v_refs ? v_ref then
      raise exception 'record_run: item ref "%" is listed twice', v_ref using errcode = '22023';
    end if;

    v_parent_id := null;
    if v_item ->> 'parent' is not null then
      v_parent_id := (v_refs ->> (v_item ->> 'parent'))::bigint;
      if v_parent_id is null then
        raise exception 'record_run: item "%" names parent "%", which is not listed before it',
          v_ref, v_item ->> 'parent' using errcode = '22023';
      end if;
      select i.kind into v_parent_kind from ledger.items i where i.id = v_parent_id;
      if (v_item ->> 'kind', v_parent_kind) not in (('story', 'lead'), ('post', 'story')) then
        raise exception 'record_run: a % cannot have a % as its parent', v_item ->> 'kind', v_parent_kind
          using errcode = '22023';
      end if;
    end if;

    insert into ledger.items as i
      (kind, pipeline, parent_id, source_table, source_id, game, format,
       channel_id, channel_type, language, title, created_at)
    values
      (v_item ->> 'kind',
       coalesce(v_item ->> 'pipeline', v_run ->> 'pipeline'),
       v_parent_id,
       v_item ->> 'source_table',
       v_item ->> 'source_id',
       v_item ->> 'game',
       v_item ->> 'format',
       v_item ->> 'channel_id',
       v_item ->> 'channel_type',
       v_item ->> 'language',
       v_item ->> 'title',
       coalesce((v_item ->> 'created_at')::timestamptz, now()))
    on conflict (source_table, source_id) do update set
      parent_id    = coalesce(i.parent_id, excluded.parent_id),
      game         = coalesce(excluded.game, i.game),
      format       = coalesce(excluded.format, i.format),
      channel_id   = coalesce(excluded.channel_id, i.channel_id),
      channel_type = coalesce(excluded.channel_type, i.channel_type),
      language     = coalesce(excluded.language, i.language),
      title        = coalesce(excluded.title, i.title),
      created_at   = least(i.created_at, excluded.created_at)
    returning * into v_row;

    if v_row.kind <> v_item ->> 'kind' then
      raise exception 'record_run: %/% already exists as a %, not a %',
        v_row.source_table, v_row.source_id, v_row.kind, v_item ->> 'kind' using errcode = '22023';
    end if;
    if v_parent_id is not null and v_row.parent_id <> v_parent_id then
      raise exception 'record_run: %/% already has a different parent',
        v_row.source_table, v_row.source_id using errcode = '22023';
    end if;

    v_refs := v_refs || jsonb_build_object(v_ref, v_row.id);
    v_touched := v_touched || v_row.id;
  end loop;

  -- 2. The run, upserted on (workflow, external_id).
  if v_run ->> 'pipeline' is null or v_run ->> 'workflow' is null
     or v_run ->> 'external_id' is null or v_run ->> 'status' is null then
    raise exception 'record_run: run needs pipeline, workflow, external_id and status' using errcode = '22023';
  end if;

  v_want_item := null;
  if v_run ->> 'item' is not null then
    v_want_item := (v_refs ->> (v_run ->> 'item'))::bigint;
    if v_want_item is null then
      raise exception 'record_run: run item "%" is not listed in items', v_run ->> 'item' using errcode = '22023';
    end if;
  end if;

  insert into ledger.runs as r
    (pipeline, workflow, external_id, workflow_version, item_id, status, outcome,
     started_at, finished_at, error_message, source, cost_recorded)
  values
    (v_run ->> 'pipeline',
     v_run ->> 'workflow',
     v_run ->> 'external_id',
     v_run ->> 'workflow_version',
     v_want_item,
     v_run ->> 'status',
     v_run ->> 'outcome',
     (v_run ->> 'started_at')::timestamptz,
     (v_run ->> 'finished_at')::timestamptz,
     v_run ->> 'error_message',
     coalesce(v_run ->> 'source', 'collector'),
     coalesce((v_run ->> 'cost_recorded')::boolean, true))
  on conflict (workflow, external_id) do update set
    -- A late or repeated "running" never moves a finished run back.
    status           = case when excluded.status = 'running' then r.status else excluded.status end,
    outcome          = coalesce(excluded.outcome, r.outcome),
    workflow_version = coalesce(excluded.workflow_version, r.workflow_version),
    item_id          = coalesce(r.item_id, excluded.item_id),
    started_at       = coalesce(r.started_at, excluded.started_at),
    finished_at      = coalesce(excluded.finished_at, r.finished_at),
    error_message    = coalesce(excluded.error_message, r.error_message),
    cost_recorded    = r.cost_recorded or excluded.cost_recorded,
    updated_at       = now()
  returning r.id, r.item_id into v_run_id, v_run_item;

  if v_want_item is not null and v_run_item <> v_want_item then
    raise exception 'record_run: run %/% is already linked to another item',
      v_run ->> 'workflow', v_run ->> 'external_id' using errcode = '22023';
  end if;
  v_touched := v_touched || v_run_item;

  -- 3. Steps. A key that already exists is skipped, so re-sending is safe.
  for v_step in select value from jsonb_array_elements(v_steps) loop
    if v_step ->> 'idempotency_key' is null or v_step ->> 'provider' is null or v_step ->> 'purpose' is null then
      raise exception 'record_run: every step needs idempotency_key, provider and purpose: %', v_step
        using errcode = '22023';
    end if;

    if v_step ->> 'item' is null then
      v_step_item := v_run_item;
    else
      v_step_item := (v_refs ->> (v_step ->> 'item'))::bigint;
      if v_step_item is null then
        raise exception 'record_run: step % names item "%", which is not listed in items',
          v_step ->> 'idempotency_key', v_step ->> 'item' using errcode = '22023';
      end if;
    end if;

    v_cost := (v_step ->> 'cost_usd')::numeric;
    v_source := v_step ->> 'cost_source';
    if v_cost is null and v_source = 'computed' then
      v_cost := (v_step ->> 'units')::numeric * (v_step ->> 'unit_price_usd')::numeric;
    end if;
    if v_source is null then
      if v_cost is not null then
        raise exception 'record_run: step % has cost_usd but no cost_source', v_step ->> 'idempotency_key'
          using errcode = '22023';
      end if;
      v_source := 'unknown';
    end if;

    insert into ledger.steps
      (run_id, item_id, idempotency_key, node, provider, model, purpose, ok, error_message,
       attempt, is_retry, superseded, cost_usd, cost_source, unit, units_in, units_out, units,
       unit_price_usd, created_at)
    values
      (v_run_id,
       v_step_item,
       v_step ->> 'idempotency_key',
       v_step ->> 'node',
       v_step ->> 'provider',
       v_step ->> 'model',
       v_step ->> 'purpose',
       coalesce((v_step ->> 'ok')::boolean, true),
       v_step ->> 'error_message',
       coalesce((v_step ->> 'attempt')::integer, 1),
       coalesce((v_step ->> 'is_retry')::boolean, false),
       coalesce((v_step ->> 'superseded')::boolean, false),
       v_cost,
       v_source,
       v_step ->> 'unit',
       (v_step ->> 'units_in')::numeric,
       (v_step ->> 'units_out')::numeric,
       (v_step ->> 'units')::numeric,
       (v_step ->> 'unit_price_usd')::numeric,
       coalesce((v_step ->> 'created_at')::timestamptz, now()))
    on conflict (idempotency_key) do nothing;

    get diagnostics v_n = row_count;
    if v_n = 1 then
      v_inserted := v_inserted + 1;
      v_touched := v_touched || v_step_item;
    else
      v_skipped := v_skipped + 1;
    end if;
  end loop;

  -- 4. Refresh the cost fields this payload touched, in the same transaction.
  perform ledger._refresh_runs(array[v_run_id]);
  perform ledger._refresh_items(array_remove(v_touched, null));

  return jsonb_build_object(
    'run_id', v_run_id,
    'steps_inserted', v_inserted,
    'steps_skipped', v_skipped,
    'items', v_refs);
end
$$;

comment on function ledger.record_run(jsonb) is
  'The only write path. Idempotent: runs upsert on (workflow, external_id), steps skip on idempotency_key. '
  'Contract: ledger/WRITE_API.md.';

-- Rebuild every cost field from steps. Used after a backfill and as a consistency check:
-- on a consistent ledger it returns {"runs_changed": 0, "items_changed": 0}.
create or replace function ledger.recompute_costs()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_runs integer;
  v_items integer;
begin
  v_runs := ledger._refresh_runs(array(select id from ledger.runs));
  v_items := ledger._refresh_items(array(select id from ledger.items where parent_id is null));
  return jsonb_build_object('runs_changed', v_runs, 'items_changed', v_items);
end
$$;

-- Thin wrapper for PostgREST RPC (`POST /rest/v1/rpc/ledger_record_run`), service role only.
create or replace function public.ledger_record_run(payload jsonb)
returns jsonb
language sql
security invoker
set search_path = ''
as $$
  select ledger.record_run(payload);
$$;

-- Functions are executable by PUBLIC by default, and Supabase also grants new functions in
-- `public` to anon and authenticated. Take all of that back, then grant exactly what is needed.
revoke all on function ledger._refresh_runs(bigint[]) from public;
revoke all on function ledger._refresh_items(bigint[]) from public;
revoke all on function ledger.record_run(jsonb) from public;
revoke all on function ledger.recompute_costs() from public;
revoke all on function public.ledger_record_run(jsonb) from public, anon, authenticated;

grant execute on function ledger.record_run(jsonb) to ledger_writer, service_role;
grant execute on function ledger.recompute_costs() to service_role;
grant execute on function public.ledger_record_run(jsonb) to service_role;
