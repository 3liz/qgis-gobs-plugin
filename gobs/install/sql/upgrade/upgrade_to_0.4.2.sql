BEGIN;

-- Unique constraint for documents
ALTER TABLE gobs.document DROP CONSTRAINT IF EXISTS document_do_label_key;
ALTER TABLE gobs.document ADD CONSTRAINT document_do_label_key UNIQUE (do_label, fk_id_indicator);

-- Add default value for import item: im_timestamp
ALTER TABLE gobs.import ALTER COLUMN im_timestamp SET DEFAULT now();

DROP TRIGGER IF EXISTS trg_manage_object_timestamps ON gobs.spatial_object;
CREATE TRIGGER trg_manage_object_timestamps
BEFORE INSERT OR UPDATE
ON gobs.spatial_object
FOR EACH ROW EXECUTE PROCEDURE gobs.manage_object_timestamps();

CREATE OR REPLACE FUNCTION gobs.find_observation_with_wrong_spatial_object(_id_series integer)
RETURNS TABLE (
    ob_uid uuid,
    so_unique_id text
)
LANGUAGE plpgsql
AS
$$
BEGIN
    RETURN QUERY
    SELECT
    o.ob_uid, s.so_unique_id
    FROM gobs.observation AS o
    INNER JOIN gobs.spatial_object AS s
        ON s.id = o.fk_id_spatial_object
    WHERE True
    -- the same series
    AND o.fk_id_series = _id_series
    -- wrong start (and optional end) dates compared to validity dates of linked spatial object
    AND (
            ob_start_timestamp
            NOT BETWEEN Coalesce('-infinity'::timestamp, so_valid_from) AND Coalesce(so_valid_to, 'infinity'::timestamp)
        OR
        (    ob_end_timestamp IS NOT NULL
            AND ob_end_timestamp
            NOT BETWEEN Coalesce('-infinity'::timestamp, so_valid_from) AND Coalesce(so_valid_to, 'infinity'::timestamp)
        )
    )
    ;

END;
$$
;

COMMENT ON FUNCTION gobs.find_observation_with_wrong_spatial_object(integer)
IS 'Find the observations with having incompatible start and end timestamp with related spatial objects validity dates'
;

CREATE OR REPLACE FUNCTION gobs.update_observations_with_wrong_spatial_objects(_id_series integer)
RETURNS TABLE (
    modified_obs_count integer,
    remaining_obs_count integer
)
LANGUAGE plpgsql
AS
$$
DECLARE
    modified_count integer;
    remaining_count integer;
BEGIN

-- Update the observations
WITH problem AS (
    SELECT *
    FROM gobs.find_observation_with_wrong_spatial_object(_id_series)
), solution AS (
    SELECT
    o.ob_uid, so.id AS new_id
    FROM
        gobs.observation AS o,
        problem AS p,
        gobs.spatial_object AS so
    WHERE True
    -- same unique id as problematic
    AND p.so_unique_id = so.so_unique_id
    -- not itself
    AND True
    -- problematic only
    AND p.ob_uid = o.ob_uid
    -- same series
    AND o.fk_id_series = _id_series
    -- same spatial layer
    AND so.fk_id_spatial_layer IN (
        SELECT fk_id_spatial_layer
        FROM gobs.series
        WHERE id = _id_series
    )
    -- compatible dates
    AND
        ob_start_timestamp
        BETWEEN Coalesce(so.so_valid_from, '-infinity'::timestamp) AND Coalesce(so.so_valid_to, 'infinity'::timestamp)
    AND (
        ob_end_timestamp IS NULL
        OR
        (    ob_end_timestamp IS NOT NULL
            AND ob_end_timestamp
            BETWEEN Coalesce(so_valid_from, '-infinity'::timestamp) AND Coalesce(so_valid_to, 'infinity'::timestamp)
        )
    )
)
UPDATE gobs.observation oo
SET fk_id_spatial_object = s.new_id
FROM solution AS s
WHERE oo.ob_uid = s.ob_uid
;

-- Get the number of rows updated
GET DIAGNOSTICS modified_count = ROW_COUNT;

-- Check if there is anything remaining
-- for example if no new id have been found to replace the wrong ones
SELECT count(*)
FROM gobs.find_observation_with_wrong_spatial_object(_id_series)
INTO remaining_count;

RETURN QUERY SELECT modified_count, remaining_count;

END;
$$
;

COMMENT ON FUNCTION gobs.update_observations_with_wrong_spatial_objects(integer)
IS 'Update observations with wrong spatial objects: it search the observation for which the start and end timestamp does not match anymore the related spatial objects validity dates. It gets the correct one if possible and perform an UPDATE for these observations. It returns a line with 2 integer columns: modified_obs_count (number of modified observations) and remaining_obs_count (number of observations still with wrong observations'
;


COMMIT;
