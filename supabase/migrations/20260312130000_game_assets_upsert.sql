-- Unique constraint for upsert from Google Sheets
ALTER TABLE game_assets
  ADD CONSTRAINT game_assets_unique_entry
  UNIQUE (game_tag, character_name, asset_type);
