-- Game Assets — centralized storage for character references, prompt blocks, images
CREATE TABLE IF NOT EXISTS game_assets (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  game_tag text NOT NULL,
  character_name text NOT NULL,
  asset_type text NOT NULL
    CHECK (asset_type IN ('reference_image','character_card','screenshot','promo_art','generated_ref')),
  url text NOT NULL,
  prompt_block text,
  tags text[],
  metadata jsonb DEFAULT '{}'
);

-- Index for quick lookups by game
CREATE INDEX idx_game_assets_game_tag ON game_assets (game_tag);

-- RLS: allow anon full access
ALTER TABLE game_assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anon full access on game_assets"
  ON game_assets
  FOR ALL
  USING (true)
  WITH CHECK (true);
