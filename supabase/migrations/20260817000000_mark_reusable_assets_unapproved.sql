-- Reusable refs are deny-by-default until a human explicitly approves the asset itself.
-- This migration does not perform visual review and does not approve any existing row.
UPDATE game_assets
SET metadata = COALESCE(metadata, '{}'::jsonb)
  || jsonb_build_object('visually_approved', false)
WHERE NOT (COALESCE(metadata, '{}'::jsonb) ? 'visually_approved');

CREATE INDEX IF NOT EXISTS idx_game_assets_visually_approved
  ON game_assets ((metadata->>'visually_approved'));
