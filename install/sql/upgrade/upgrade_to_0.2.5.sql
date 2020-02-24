
ALTER TABLE gobs.observation DROP CONSTRAINT IF EXISTS observation_data_unique;
ALTER TABLE gobs.observation
ADD CONSTRAINT observation_data_unique UNIQUE (fk_id_series, fk_id_spatial_object, ob_timestamp);

ALTER TABLE gobs.observation ADD COLUMN IF NOT EXISTS ob_validation timestamp;
COMMENT ON COLUMN gobs.observation.ob_validation IS 'Date and time when the data has been validated (the corresponding import status has been changed from pending to validated). Can be used to find all observations not yet validated, with NULL values in this field.';

-- Validation triggers
CREATE OR REPLACE FUNCTION gobs.trg_after_import_validation()
RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
DECLARE
    _output integer;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.im_status = 'V' AND NEW.im_status != OLD.im_status THEN
        UPDATE gobs.observation
        SET ob_validation = now()
        WHERE TRUE
        AND fk_id_import = NEW.id
        ;
    END IF;

    RETURN NEW;
END;
$$
;
DROP TRIGGER IF EXISTS gobs_on_import_change ON gobs.import;
CREATE TRIGGER gobs_on_import_change
AFTER UPDATE ON gobs.import
FOR EACH ROW EXECUTE PROCEDURE gobs.trg_after_import_validation();

