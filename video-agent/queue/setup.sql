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
-- Game Assets — каталог персонажей и ассетов
-- ============================================

CREATE TABLE IF NOT EXISTS game_assets (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  game_tag text NOT NULL,
  character_name text,
  asset_type text NOT NULL
    CHECK (asset_type IN ('reference_image','character_card','screenshot','promo_art','generated_ref')),
  url text,
  prompt_block text,
  tags text[],
  metadata jsonb DEFAULT '{}'
);

CREATE INDEX idx_game_assets_game_tag ON game_assets (game_tag);

ALTER TABLE game_assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon full access on game_assets"
  ON game_assets
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- ============================================
-- video_agent_runs: каталог сгенерированных видео.
-- Добавляем формат + youtube_url + UNIQUE на output_video_url,
-- чтобы регенерация в тот же путь обновляла строку (upsert), а не плодила дубли.
-- Пишется из queue/log-video.sh. title маппится на input_idea.
-- ============================================

ALTER TABLE video_agent_runs ADD COLUMN IF NOT EXISTS format text;
ALTER TABLE video_agent_runs ADD COLUMN IF NOT EXISTS youtube_url text;
ALTER TABLE video_agent_runs DROP CONSTRAINT IF EXISTS video_agent_runs_output_url_key;
ALTER TABLE video_agent_runs ADD CONSTRAINT video_agent_runs_output_url_key UNIQUE (output_video_url);

-- ============================================
-- Supabase Storage: создай buckets вручную
-- Dashboard → Storage → New Bucket → Name: "videos" → Public: ON
-- Dashboard → Storage → New Bucket → Name: "assets" → Public: ON
-- ============================================

-- ============================================
-- Migration: расширение asset_type для gameplay и аватаров
-- ============================================

ALTER TABLE game_assets DROP CONSTRAINT IF EXISTS game_assets_asset_type_check;
ALTER TABLE game_assets ADD CONSTRAINT game_assets_asset_type_check
  CHECK (asset_type IN (
    'reference_image',   -- Character ref (PNG)
    'character_card',    -- Promo card
    'screenshot',        -- In-game screenshot
    'promo_art',         -- Official art
    'generated_ref',     -- AI-generated ref
    'avatar_ref',        -- AI avatar для gameplay-ai-avatar формата
    'gameplay_clip'      -- Gameplay recording (MP4)
  ));

-- ============================================
-- Storage structure (reference):
--
-- Бакет "assets" (медиа-ассеты, зеркалит локальную games/):
--   assets/{GAME_TAG}/gameplay/{filename}.mp4
--   assets/{GAME_TAG}/refs/{character-name}.png
--   assets/{GAME_TAG}/avatars/{avatar-name}.png
--
-- Бакет "videos" (финальные видео по датам):
--   videos/{GAME_TAG}/{YYYY-MM-DD}/{format}_final.mp4
--
-- Бакет "music" (фоновые треки):
--   music/{track-name}.mp3
-- ============================================

-- ============================================
-- Migration: agent_plan/approach_used/model_used → yt/tt/inst published timestamps
-- Run once in Supabase SQL Editor:
-- https://supabase.com/dashboard/project/txckerrkubbvmzlionjf/sql
-- ============================================

ALTER TABLE video_agent_runs RENAME COLUMN agent_plan    TO yt_published;
ALTER TABLE video_agent_runs RENAME COLUMN approach_used TO tt_published;
ALTER TABLE video_agent_runs RENAME COLUMN model_used    TO inst_published;

ALTER TABLE video_agent_runs ALTER COLUMN yt_published   TYPE timestamptz USING NULL;
ALTER TABLE video_agent_runs ALTER COLUMN tt_published   TYPE timestamptz USING NULL;
ALTER TABLE video_agent_runs ALTER COLUMN inst_published TYPE timestamptz USING NULL;

-- Index for mobile-mcp agent: find oldest video not yet published to a platform
CREATE INDEX IF NOT EXISTS idx_runs_tt_unpublished
  ON video_agent_runs (created_at ASC) WHERE tt_published IS NULL;
CREATE INDEX IF NOT EXISTS idx_runs_inst_unpublished
  ON video_agent_runs (created_at ASC) WHERE inst_published IS NULL;
