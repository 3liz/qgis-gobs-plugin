-- Add restrictions when editing observation data
ALTER TABLE gobs.protocol ADD COLUMN IF NOT EXISTS pr_days_editable integer NOT NULL DEFAULT 30;
COMMENT ON COLUMN gobs.protocol.pr_days_editable
IS 'Number of days the observations from series related to the protocol are editable (delete & update) after creation.
Use a very long value such as 10000 if the editing can occur at any time.
The control is made based on the observation created_at column';

-- Trigger qui contrôle cela selon certaines conditions
CREATE OR REPLACE FUNCTION gobs.control_observation_editing_capability()
RETURNS TRIGGER  AS $trg$
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
$trg$
LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_control_observation_editing_capability ON gobs.observation;
CREATE TRIGGER trg_control_observation_editing_capability
BEFORE UPDATE OR DELETE ON gobs.observation
FOR EACH ROW EXECUTE PROCEDURE gobs.control_observation_editing_capability();


-- Correction d'une valeur par défaut
ALTER TABLE gobs.spatial_layer ALTER COLUMN sl_creation_date SET DEFAULT now()::date;
