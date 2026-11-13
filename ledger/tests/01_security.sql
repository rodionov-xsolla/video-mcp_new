-- Security: RLS on, no policies, anon and authenticated refused everywhere, writer and reader
-- limited to exactly what they need.
begin;
create extension if not exists pgtap with schema extensions;
select plan(31);

-- Tables, RLS, policies
select has_table('ledger', 'items', 'ledger.items exists');
select has_table('ledger', 'runs', 'ledger.runs exists');
select has_table('ledger', 'steps', 'ledger.steps exists');
select ok((select relrowsecurity from pg_class where oid = 'ledger.items'::regclass), 'RLS is on for items');
select ok((select relrowsecurity from pg_class where oid = 'ledger.runs'::regclass), 'RLS is on for runs');
select ok((select relrowsecurity from pg_class where oid = 'ledger.steps'::regclass), 'RLS is on for steps');
select is((select count(*)::integer from pg_policies where schemaname = 'ledger'), 0, 'ledger has no RLS policies');

-- anon and authenticated: nothing
select ok(not has_schema_privilege('anon', 'ledger', 'usage'), 'anon has no access to the ledger schema');
select ok(not has_schema_privilege('authenticated', 'ledger', 'usage'), 'authenticated has no access to the ledger schema');
select ok(not has_function_privilege('anon', 'public.ledger_record_run(jsonb)', 'execute'), 'anon cannot execute the RPC wrapper');
select ok(not has_function_privilege('authenticated', 'public.ledger_record_run(jsonb)', 'execute'), 'authenticated cannot execute the RPC wrapper');

-- writer: the write function only
select ok(has_function_privilege('ledger_writer', 'ledger.record_run(jsonb)', 'execute'), 'writer can call record_run');
select ok(not has_table_privilege('ledger_writer', 'ledger.items', 'select'), 'writer cannot read items directly');
select ok(not has_table_privilege('ledger_writer', 'ledger.steps', 'insert'), 'writer cannot insert steps directly');
select ok(not has_function_privilege('ledger_writer', 'ledger.recompute_costs()', 'execute'), 'writer cannot run recompute_costs');

-- reader: the views only
select ok(not has_table_privilege('ledger_reader', 'ledger.items', 'select'), 'reader cannot read the items table');
select ok(not has_table_privilege('ledger_reader', 'ledger.runs', 'select'), 'reader cannot read the runs table');
select ok(not has_table_privilege('ledger_reader', 'ledger.steps', 'select'), 'reader cannot read the steps table');
select is(
  (select count(*)::integer
     from pg_class c
     join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'ledger' and c.relkind = 'v'
      and not has_table_privilege('ledger_reader', c.oid, 'select')),
  0, 'reader can read every ledger view');
select ok(not has_function_privilege('ledger_reader', 'ledger.record_run(jsonb)', 'execute'), 'reader cannot write');

-- internal helpers are not callable by anyone but their owner
select ok(not has_function_privilege('service_role', 'ledger._refresh_items(bigint[])', 'execute'), 'helpers are not public');

-- Real refusals, not just catalog answers
set local role anon;
select throws_ok($$select count(*) from ledger.items$$, '42501', null, 'anon reading items is refused');
select throws_ok($$select count(*) from ledger.v_items$$, '42501', null, 'anon reading a view is refused');
select throws_ok($$select public.ledger_record_run('{}'::jsonb)$$, '42501', null, 'anon calling the RPC wrapper is refused');
reset role;

set local role authenticated;
select throws_ok($$select count(*) from ledger.runs$$, '42501', null, 'authenticated reading runs is refused');
select throws_ok($$select public.ledger_record_run('{}'::jsonb)$$, '42501', null, 'authenticated calling the RPC wrapper is refused');
reset role;

set local role service_role;
select lives_ok(
  $$select public.ledger_record_run(
      '{"run": {"pipeline": "content", "workflow": "probe", "external_id": "1", "status": "succeeded"}}'::jsonb)$$,
  'service role can record a run through the RPC wrapper');
select throws_ok($$select count(*) from ledger.runs$$, '42501', null, 'service role still cannot read tables directly');
reset role;

grant usage on schema extensions to ledger_reader;
grant ledger_reader to postgres;
set local role ledger_reader;
select is((select count(*)::integer from ledger.v_runs), 1, 'reader sees the recorded run through v_runs');
select throws_ok($$select count(*) from ledger.runs$$, '42501', null, 'reader reading the runs table is refused');
select throws_ok($$select ledger.record_run('{}'::jsonb)$$, '42501', null, 'reader calling record_run is refused');
reset role;

select * from finish();
rollback;
