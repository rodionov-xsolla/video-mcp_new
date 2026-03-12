-- Make character_name and url nullable for assets without images or game-wide assets
ALTER TABLE game_assets ALTER COLUMN character_name DROP NOT NULL;
ALTER TABLE game_assets ALTER COLUMN url DROP NOT NULL;
