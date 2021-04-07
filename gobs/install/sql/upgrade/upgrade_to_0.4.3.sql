BEGIN;

-- actor_category
ALTER TABLE gobs.actor_category DROP CONSTRAINT IF EXISTS actor_category_ac_label_key;
ALTER TABLE gobs.actor_category ADD UNIQUE (ac_label);

-- actor
ALTER TABLE gobs.actor ADD COLUMN IF NOT EXISTS a_login text UNIQUE;

UPDATE gobs.actor SET a_login = replace(lower(trim(a_label)), ' ', '_') WHERE a_login IS NULL;
ALTER TABLE gobs.actor ALTER COLUMN a_login SET NOT NULL;
COMMENT ON COLUMN gobs.actor.a_login IS 'Login of the actor. It is the unique identifier of the actor.';



COMMIT;
