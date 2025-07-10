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
AND o.fk_id_actor IS NULL
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
-- Add a project id if needed (for test migrations we had no project data)
INSERT INTO gobs.project
(id, pt_code, pt_lizmap_project_key, pt_label, pt_description, pt_indicator_codes)
SELECT
1, 'test_project_a', NULL, 'GobsAPI test project a', 'Test project a', '{pluviometry,population}'
WHERE NOT EXISTS (
    SELECT id
    FROM gobs.project
    WHERE id = 1
)
;

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

DROP FUNCTION IF EXISTS gobs.get_spatial_layer_vector_data(integer, date);
CREATE OR REPLACE FUNCTION gobs.get_spatial_layer_vector_data(
    spatial_layer_id integer,
    validity_date date
)
RETURNS TABLE (
    id integer,
    code text,
    label text,
    uid text,
    valid_from date,
    valid_to date,
    id_actor integer,
    geom public.geometry(geometry, 4326)
) AS
$FUNCTION$
DECLARE
    _spatial_layer record;
    _sql_text text;
BEGIN
    -- Get spatial layer data
    SELECT INTO _spatial_layer
        *
    FROM gobs.spatial_layer AS sl
    WHERE sl.id = spatial_layer_id;

    IF _spatial_layer.id IS NULL THEN
        RAISE EXCEPTION 'G-Obs - No spatial layer found for the given ID %',
            spatial_layer_id
        ;
    END IF;

    -- Build SQL
    _sql_text = format(
        $sql$
        SELECT
            so.id,
            so.so_unique_id AS code,
            so.so_unique_label AS label,
            so.so_uid::text AS uid,
            so.so_valid_from AS valid_from,
            so.so_valid_to AS valid_to,
            so.fk_id_actor AS id_actor,
            so.geom::public.geometry(%1$s, 4326) AS geom
        FROM gobs.spatial_object AS so
        WHERE so.fk_id_spatial_layer = %2$s
        $sql$,
        _spatial_layer.sl_geometry_type,
        _spatial_layer.id
    )
    ;

    -- Add optionnal date filter
    IF validity_date IS NOT NULL THEN
        _sql_text = _sql_text || format(
            $sql$
            AND
                (
                    (so_valid_from IS NULL OR so_valid_from <= '%1$s'::date)
                    AND
                    (so_valid_to IS NULL OR so_valid_to > '%1$s'::date)
                )
            $sql$,
            validity_date::text
        );

    END IF;

    RETURN QUERY
    EXECUTE _sql_text
    ;
END;

$FUNCTION$
LANGUAGE plpgsql
;

COMMENT ON FUNCTION gobs.get_spatial_layer_vector_data(integer, date)
IS 'Get the spatial object vector data corresponding to the given spatial layer ID.
A date can be given to restrict objects corresponding to this date.'
;

DROP FUNCTION IF EXISTS gobs.get_series_data(integer, boolean);

CREATE OR REPLACE FUNCTION gobs.get_series_data(
	series_id integer,
	add_geometry boolean)
    RETURNS TABLE(id integer, spatial_object_code text, geom public.geometry, observation_start text, observation_end text, observation_start_timestamp timestamp without time zone, observation_end_timestamp timestamp without time zone, observation_values json, id_actor integer)
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    _series_data record;
    _sql_text text;
    _date_formater text;
    _date_format_rules jsonb;
    _get_values record;
    _values_array text[];
    _values_text text;
BEGIN
    -- Get series data
    SELECT INTO _series_data
        s.id,
        i.id_label,
        i.id_date_format,
        array_agg(d.di_code ORDER BY d.id) AS id_value_codes,
        array_agg(d.di_type ORDER BY d.id) AS id_value_types,
        array_agg(d.di_unit ORDER BY d.id) AS id_value_units
    FROM gobs.indicator AS i
    INNER JOIN gobs.dimension AS d
        ON d.fk_id_indicator = i.id
    INNER JOIN gobs.series AS s
        ON s.fk_id_indicator = i.id
    WHERE s.id = series_id
    GROUP BY s.id, id_label, id_date_format
    ;

    IF _series_data.id IS NULL THEN
        RAISE EXCEPTION 'G-Obs - No series found for the given ID %',
            series_id
        ;
    END IF;

    -- Get date formatter
    _date_formater = 'YYYY-MM-DD HH24:MI:SS';
    _date_format_rules = json_build_object(
        'second', 'YYYY-MM-DD HH24:MI:SS',
        'minute', 'YYYY-MM-DD HH24:MI',
        'hour', 'YYYY-MM-DD HH24',
        'day', 'YYYY-MM-DD',
        'month', 'YYYY-MM',
        'year', 'YYYY'
    );
    IF _date_format_rules ? _series_data.id_date_format THEN
        _date_formater = _date_format_rules->>(_series_data.id_date_format);
    END IF;

    -- Get observation values SELECT clause
    FOR _get_values IN
        SELECT
            row_number() OVER() AS idx,
            code
        FROM unnest(_series_data.id_value_codes) AS code
    LOOP
        _values_array = array_append(
            _values_array,
            format( $TEXT$ '%1$s', (ob_value->>%2$s)::%3$s $TEXT$,
                _series_data.id_value_codes[_get_values.idx],
                _get_values.idx - 1,
                _series_data.id_value_types[_get_values.idx]
            )
        );
    END LOOP;
    _values_text = concat(
        'json_build_object(',
        array_to_string(_values_array, ', '),
        ')'
    );

    -- Build SQL
    _sql_text = format(
        $sql$
        SELECT
            o.id,
            so_unique_id AS spatial_object_code,
            %1$s,
            to_char(ob_start_timestamp, '%2$s') AS observation_start,
            to_char(ob_end_timestamp, '%2$s') AS observation_end,
            ob_start_timestamp AS observation_start_timestamp,
            ob_end_timestamp AS observation_end_timestamp,
            %3$s,
            o.fk_id_actor AS id_actor
        FROM gobs.observation AS o
        INNER JOIN gobs.spatial_object AS so
        ON so.id = o.fk_id_spatial_object
        WHERE fk_id_series = %4$s

        $sql$,
        -- add the geometry column if needed
        CASE
            WHEN add_geometry IS TRUE THEN 'so.geom'
            ELSE 'NULL::public.geometry AS geom'
        END,
        -- Date formater
        _date_formater,
        -- Indicator values
        _values_text,
        -- Series ID
        _series_data.id
    )
    ;

    RAISE NOTICE '%', _sql_text;

    RETURN QUERY
    EXECUTE _sql_text
    ;
END;

$BODY$;

COMMENT ON FUNCTION gobs.get_series_data(integer, boolean)
    IS 'Get the given series observation data, with optional geometry.';


-- TODO AJOUTER UNE CONTRAINTE SUR LES DIMENSIONS et les observation existantes
-- aujourd'hui, on peut très bien supprimer ou ajouter une dimension à un indicator
-- Dans la table observation, on enregistre les valeurs comme un array
-- il faut absolument empecher toute modification de dimensions une fois que des données existent
-- il faut aussi toujours vérifier que l'ordre des dimensions est utilisés dans les fonctions d'aggrégats et de stockage des valeurs : voir API PHP ET QGIS
