-- OBSERVATION: ADD AND POPULATE NEW COLUMN FK_ID_ACTOR
-- column
ALTER TABLE gobs.observation ADD COLUMN IF NOT EXISTS fk_id_actor integer;
COMMENT ON COLUMN gobs.observation.fk_id_actor IS 'Actor, source of the observation data.';
-- trigger off
ALTER TABLE gobs.observation DISABLE TRIGGER trg_control_observation_editing_capability;
ALTER TABLE gobs.observation DISABLE TRIGGER trg_manage_object_timestamps;
-- update
UPDATE gobs.observation AS o
SET fk_id_actor = s.fk_id_actor
FROM gobs.series AS s
WHERE o.fk_id_series = s.id
;
-- fk
ALTER TABLE gobs.observation DROP CONSTRAINT IF EXISTS "observation_fk_id_actor_fkey";
ALTER TABLE gobs.observation ADD CONSTRAINT "observation_fk_id_actor_fkey"
FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT
;
-- not null
ALTER TABLE gobs.observation ALTER COLUMN fk_id_actor SET NOT NULL;
-- index
DROP INDEX IF EXISTS gobs.observation_fk_id_actor_idx;
CREATE INDEX observation_fk_id_actor_idx ON gobs.observation (fk_id_actor)
;
-- series: remove the column fk_id_actor
ALTER TABLE gobs.series DROP COLUMN IF EXISTS fk_id_actor;


-- series : merge similar series
WITH grouped AS (
    -- Get the series grouped with the same protocol, indicator & spatial layer
    SELECT
        fk_id_protocol, fk_id_indicator, fk_id_spatial_layer,
        array_agg(id ORDER BY id) AS ids_series,
        min(id) AS min_id_series
    FROM gobs.series
    GROUP BY fk_id_protocol, fk_id_indicator, fk_id_spatial_layer
),
up AS (
    -- Update observations having a series id which is not the first
    -- put the first id_series instead
    UPDATE gobs.observation AS o
    SET fk_id_series = g.min_id_series
    FROM grouped AS g
    WHERE o.fk_id_series = ANY (g.ids_series)
    AND o.fk_id_series != g.min_id_series
)
-- DELETE useless series
DELETE FROM gobs.series
WHERE id NOT IN (
    SELECT min_id_series
    FROM grouped
)
;
-- trigger on
ALTER TABLE gobs.observation ENABLE TRIGGER trg_control_observation_editing_capability;
ALTER TABLE gobs.observation ENABLE TRIGGER trg_manage_object_timestamps;


-- SERIES: ADD A PROJECT ID COLUMN
ALTER TABLE gobs.series ADD COLUMN IF NOT EXISTS fk_id_project integer;
COMMENT ON COLUMN gobs.series.fk_id_project IS 'Project of the given series';
WITH s AS (
    SELECT i.id AS indicator_id, i.id_code, i.id_label, s.id AS series_id
    FROM gobs.indicator AS i
    JOIN gobs.series AS s
        ON s.fk_id_indicator = i.id
),
u AS (
    SELECT
        p.id, pt_label,
        unnest(pt_indicator_codes) AS indicator
    FROM gobs.project AS p
), final AS (
    SELECT
        min(u.id) AS project_id, series_id
    FROM u JOIN s ON indicator = s.id_code
    GROUP BY series_id
)
UPDATE gobs.series AS s
SET fk_id_project = f.project_id
FROM final AS f
WHERE s.id = f.series_id
;
ALTER TABLE gobs.series ALTER COLUMN fk_id_project SET NOT NULL;
ALTER TABLE gobs.series
ADD CONSTRAINT "series_fk_id_project_fkey"
FOREIGN KEY (fk_id_project) REFERENCES gobs.project(id)
ON DELETE RESTRICT;
DROP INDEX IF EXISTS gobs.series_fk_id_project_idx;
CREATE INDEX series_fk_id_project_idx ON gobs.series (fk_id_project);

-- project: drop column pt_indicator_codes
ALTER TABLE gobs.project DROP COLUMN IF EXISTS pt_indicator_codes;


-- SPATIAL LAYER & OBJECT - Move fk_id_actor from spatial layer to spatial object
-- column
ALTER TABLE gobs.spatial_object ADD COLUMN IF NOT EXISTS fk_id_actor integer;
COMMENT ON COLUMN gobs.spatial_object.fk_id_actor IS 'Actor, source of the spatial object data.';
-- trigger off
ALTER TABLE gobs.spatial_object DISABLE TRIGGER trg_manage_object_timestamps;
ALTER TABLE gobs.spatial_object DISABLE TRIGGER trg_update_observation_on_spatial_object_change;
ALTER TABLE gobs.spatial_object DISABLE TRIGGER trg_update_spatial_object_end_validity;
-- update
UPDATE gobs.spatial_object AS o
SET fk_id_actor = l.fk_id_actor
FROM gobs.spatial_layer AS l
WHERE o.fk_id_spatial_layer = l.id
;
-- trigger on
ALTER TABLE gobs.spatial_object ENABLE TRIGGER trg_manage_object_timestamps;
ALTER TABLE gobs.spatial_object ENABLE TRIGGER trg_update_observation_on_spatial_object_change;
ALTER TABLE gobs.spatial_object ENABLE TRIGGER trg_update_spatial_object_end_validity;
-- fk
ALTER TABLE gobs.spatial_object
ADD CONSTRAINT "spatial_object_fk_id_actor_fkey"
FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT
;
-- not null
ALTER TABLE gobs.spatial_object ALTER COLUMN fk_id_actor SET NOT NULL;
-- index
CREATE INDEX ON gobs.spatial_object (fk_id_actor);
-- drop column
ALTER TABLE gobs.spatial_layer DROP COLUMN IF EXISTS fk_id_actor;
