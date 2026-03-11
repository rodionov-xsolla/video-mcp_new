-- Video Tasks Queue — выполнить в Supabase SQL Editor
-- https://supabase.com/dashboard/project/txckerrkubbvmzlionjf/sql

CREATE TABLE video_tasks (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  game_tag text NOT NULL,
  idea text NOT NULL,
  priority integer DEFAULT 0,
  source text DEFAULT 'manual',
  source_row_id text,
  status text DEFAULT 'pending'
    CHECK (status IN ('pending','running','completed','failed','cancelled')),
  claimed_at timestamptz,
  completed_at timestamptz,
  output_video_url text,
  error_message text,
  retry_count integer DEFAULT 0,
  max_retries integer DEFAULT 2
);

-- Индекс для быстрого поиска pending задач
CREATE INDEX idx_video_tasks_pending
  ON video_tasks (status, priority DESC, created_at ASC)
  WHERE status = 'pending';

-- RLS: разрешить anon-ключу читать и писать
ALTER TABLE video_tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon full access"
  ON video_tasks
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- ============================================
-- Video Agent Runs — лог всех генераций
-- ============================================

CREATE TABLE IF NOT EXISTS video_agent_runs (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  game_tag text NOT NULL,
  input_idea text NOT NULL,
  agent_plan text,
  approach_used integer,
  model_used text,
  total_cost_usd numeric(8,4),
  output_video_url text,
  status text DEFAULT 'running'
    CHECK (status IN ('running','completed','failed')),
  error_message text,
  video_duration_seconds integer,
  run_duration_seconds integer,
  scenes jsonb
);

ALTER TABLE video_agent_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon full access on runs"
  ON video_agent_runs
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- ============================================
-- Supabase Storage: создай bucket вручную
-- Dashboard → Storage → New Bucket → Name: "videos" → Public: ON
-- ============================================
