-- Remove table application
DROP TABLE IF EXISTS gobs.application;

-- Modify actor categories
UPDATE gobs.actor SET id_category = 1;
UPDATE gobs.actor SET id_category = 2
WHERE a_description ILIKE '%Automatically created%'
;

-- Modify categories
UPDATE gobs.actor_category
SET (ac_label, ac_description) = ('other', 'Other actors')
WHERE id = 1
;
UPDATE gobs.actor_category
SET (ac_label, ac_description) = ('platform_user', 'Platform users')
WHERE id = 2
;

-- Delete obsolete categories
DELETE FROM gobs.actor_category WHERE id > 2;
SELECT setval(pg_get_serial_sequence('"gobs"."actor_category"', 'id'), (SELECT max("id") FROM "gobs"."actor_category"));
SELECT setval(pg_get_serial_sequence('"gobs"."actor"', 'id'), (SELECT max("id") FROM "gobs"."actor"));

-- Remove not null on actor login
ALTER TABLE gobs.actor ALTER COLUMN a_login DROP NOT NULL;
COMMENT ON COLUMN gobs.actor.a_login
IS $$Login of the actor. It is the unique identifier of the actor. Only needed for actors having the category 'platform_user'.$$
;

-- spatial layer
ALTER TABLE gobs.spatial_layer ALTER COLUMN sl_creation_date SET DEFAULT (now())::date;

-- dimension
ALTER TABLE gobs.dimension
ALTER COLUMN fk_id_indicator SET NOT NULL
;

-- protocoles
ALTER TABLE gobs.protocol
ADD COLUMN IF NOT EXISTS pr_days_editable integer DEFAULT 30 NOT NULL
;

COMMENT ON COLUMN gobs.protocol.pr_days_editable
IS 'Number of days the observations from series related to the protocol are editable (delete & update) after creation.
Use a very long value such as 10000 if the editing can occur at any time.
The control is made based on the observation created_at column';


-- control_observation_editing_capability()
CREATE OR REPLACE FUNCTION gobs.control_observation_editing_capability() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    maximum_duration integer;
    observation_ok boolean;
    can_edit_protocol boolean;
BEGIN
    -- Do nothing for creation
    IF TG_OP = 'INSERT' THEN
        RETURN NEW;
    END IF;

    -- If the current user has the right to edit the protocol, do not restrict editing
    can_edit_protocol = (
        SELECT (count(*) > 0)
        FROM information_schema.role_table_grants
        WHERE grantee = current_role
        AND table_schema = 'gobs'
        AND table_name = 'protocol'
        AND privilege_type IN ('UPDATE', 'INSERT')
    );
    IF can_edit_protocol THEN
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NEW;
        END IF;
    END IF;

    -- Get the protocol delay
    maximum_duration := (
        SELECT pr_days_editable
        FROM gobs.protocol
        WHERE id IN (
            SELECT fk_id_protocol
            FROM gobs.series
            WHERE id = NEW.fk_id_series
        )
        LIMIT 1
    );

    -- Check the observation created_at timestamp agains the maximum duration in days
    observation_ok = ((now() - NEW.created_at) < (concat(maximum_duration, ' days'))::interval);

    IF NOT observation_ok THEN
        -- On renvoie une erreur
        RAISE EXCEPTION 'The given observation cannot be edited since it is older than the delay defined in its related series protocol';
    END IF;

    -- If no problem occured, return the record
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;

DROP TRIGGER IF EXISTS trg_control_observation_editing_capability ON gobs.observation;
CREATE TRIGGER trg_control_observation_editing_capability
BEFORE DELETE OR UPDATE ON gobs.observation FOR EACH ROW
EXECUTE PROCEDURE gobs.control_observation_editing_capability();


INSERT INTO gobs.glossary (gl_field, gl_code, gl_label, gl_description, gl_order)
VALUES
('pv_type', 'global', 'Global', 'Global project view (only one per project)', 1),
('pv_type', 'filter', 'Filter', 'Filter view (to restrict access to some observations)', 2)
WHERE NOT EXISTS (
    SELECT id FROM gobs.glossary WHERE gl_field = 'pv_type'
)
ON CONFLICT DO NOTHING;
