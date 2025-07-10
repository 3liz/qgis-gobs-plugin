--
-- PostgreSQL database dump
--




SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- control_observation_editing_capability()
CREATE FUNCTION gobs.control_observation_editing_capability() RETURNS trigger
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


-- find_observation_with_wrong_spatial_object(integer)
CREATE FUNCTION gobs.find_observation_with_wrong_spatial_object(_id_series integer) RETURNS TABLE(ob_uid uuid, so_unique_id text)
    LANGUAGE plpgsql
    AS $$
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
$$;


-- FUNCTION find_observation_with_wrong_spatial_object(_id_series integer)
COMMENT ON FUNCTION gobs.find_observation_with_wrong_spatial_object(_id_series integer) IS 'Find the observations with having incompatible start and end timestamp with related spatial objects validity dates';


-- get_series_data(integer, boolean)
CREATE FUNCTION gobs.get_series_data(series_id integer, add_geometry boolean) RETURNS TABLE(id integer, spatial_object_code text, geom public.geometry, observation_start text, observation_end text, observation_start_timestamp timestamp without time zone, observation_end_timestamp timestamp without time zone, observation_values json, id_actor integer)
    LANGUAGE plpgsql
    AS $_$
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
            ELSE 'NULL::geometry AS geom'
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

$_$;


-- FUNCTION get_series_data(series_id integer, add_geometry boolean)
COMMENT ON FUNCTION gobs.get_series_data(series_id integer, add_geometry boolean) IS 'Get the given series observation data, with optional geometry.';


-- get_spatial_layer_vector_data(integer, date)
CREATE FUNCTION gobs.get_spatial_layer_vector_data(spatial_layer_id integer, validity_date date) RETURNS TABLE(id integer, code text, label text, uid text, valid_from date, valid_to date, id_actor integer, geom public.geometry)
    LANGUAGE plpgsql
    AS $_$
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
            so.geom::geometry(%1$s, 4326) AS geom
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

$_$;


-- FUNCTION get_spatial_layer_vector_data(spatial_layer_id integer, validity_date date)
COMMENT ON FUNCTION gobs.get_spatial_layer_vector_data(spatial_layer_id integer, validity_date date) IS 'Get the spatial object vector data corresponding to the given spatial layer ID.
A date can be given to restrict objects corresponding to this date.';


-- log_deleted_object()
CREATE FUNCTION gobs.log_deleted_object() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    oid text;
BEGIN
    INSERT INTO gobs.deleted_data_log (
        de_table,
        de_uid,
        de_timestamp
    )
    VALUES (
        TG_TABLE_NAME::text,
        OLD.ob_uid,
        now()
    )
    ;
    RETURN OLD;
END;
$$;


-- manage_object_timestamps()
CREATE FUNCTION gobs.manage_object_timestamps() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    nowtm timestamp;
BEGIN
    nowtm = now();
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = nowtm;
        NEW.updated_at = nowtm;
    END IF;

    IF TG_OP = 'UPDATE' THEN
        NEW.updated_at = nowtm;
    END IF;

    RETURN NEW;
END;
$$;


-- parse_indicator_paths(integer, text)
CREATE FUNCTION gobs.parse_indicator_paths(i_id integer, i_path text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    _path text;
    _group text;
    _word text;
    _parent text;
    _gid integer;
    _leaf text;
    _leaves text[];
BEGIN
    _parent = NULL;

    -- PARSE PATHS
    -- Insert root
    INSERT INTO gobs.graph_node (gn_label)
    VALUES ('ROOT')
    ON CONFLICT DO NOTHING;

    -- Explode path
    FOR _group IN
        SELECT trim(g)
        FROM regexp_split_to_table(i_path, ',') AS g
    LOOP
        RAISE NOTICE 'groupe = "%" ', _group;
        -- Explode group
        FOR _word IN
            SELECT trim(w) AS w
            FROM regexp_split_to_table(_group, '/') AS w
        LOOP
            RAISE NOTICE '  * word = "%", parent = "%" ', _word, _parent;

            -- gobs.graph_node
            INSERT INTO gobs.graph_node (gn_label)
            VALUES (_word)
            ON CONFLICT (gn_label)
            DO NOTHING
            RETURNING id
            INTO _gid;
            IF _gid IS NULL THEN
                SELECT id INTO _gid
                FROM gobs.graph_node
                WHERE gn_label = _word;
            END IF;

            -- gobs.r_graph_edge
            INSERT INTO gobs.r_graph_edge (ge_parent_node, ge_child_node)
            VALUES (
                (SELECT id FROM gobs.graph_node WHERE gn_label = coalesce(_parent, 'ROOT') LIMIT 1),
                _gid
            )
            ON CONFLICT DO NOTHING;

            -- Change parent with current word -> Next will have it as parent
            _parent =  _word;

            -- store leaf
            _leaf = _word;

        END LOOP;
        -- Put back parent to NULL -> next will start with ROOT
        _parent =  NULL;

        -- Add leaf to leaves
        _leaves = _leaves || _leaf ;
        _leaf = NULL;
    END LOOP;

    -- Add leaves to r_indicator_node
    RAISE NOTICE '  leaves % ', _leaves;

    INSERT INTO gobs.r_indicator_node
    (fk_id_indicator, fk_id_node)
    SELECT i_id, (
        SELECT id FROM gobs.graph_node WHERE gn_label = leaf LIMIT 1
    )
    FROM (
        SELECT unnest(_leaves) AS leaf
    ) AS source
    ON CONFLICT DO NOTHING;

    RETURN 1;
END;
$$;


-- trg_after_import_validation()
CREATE FUNCTION gobs.trg_after_import_validation() RETURNS trigger
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
$$;


-- trg_parse_indicator_paths()
CREATE FUNCTION gobs.trg_parse_indicator_paths() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    _output integer;
BEGIN
    IF TG_OP = 'INSERT' OR NEW.id_paths != OLD.id_paths THEN
        SELECT gobs.parse_indicator_paths(NEW.id, NEW.id_paths)
        INTO _output;
    END IF;

    RETURN NEW;
END;
$$;


-- update_observation_on_spatial_object_change()
CREATE FUNCTION gobs.update_observation_on_spatial_object_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NOT ST_Equals(NEW.geom, OLD.geom) THEN
        UPDATE gobs.observation
        SET updated_at = now()
        WHERE fk_id_spatial_object = NEW.id
        ;
    END IF;

    RETURN NEW;
END;
$$;


-- update_observations_with_wrong_spatial_objects(integer)
CREATE FUNCTION gobs.update_observations_with_wrong_spatial_objects(_id_series integer) RETURNS TABLE(modified_obs_count integer, remaining_obs_count integer)
    LANGUAGE plpgsql
    AS $$
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
$$;


-- FUNCTION update_observations_with_wrong_spatial_objects(_id_series integer)
COMMENT ON FUNCTION gobs.update_observations_with_wrong_spatial_objects(_id_series integer) IS 'Update observations with wrong spatial objects: it search the observation for which the start and end timestamp does not match anymore the related spatial objects validity dates. It gets the correct one if possible and perform an UPDATE for these observations. It returns a line with 2 integer columns: modified_obs_count (number of modified observations) and remaining_obs_count (number of observations still with wrong observations';


-- update_spatial_object_end_validity()
CREATE FUNCTION gobs.update_spatial_object_end_validity() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    nowtm timestamp;
    last_id integer;
BEGIN
    last_id = 0;
    IF TG_OP = 'INSERT' THEN

        -- Get the last corresponding item
        SELECT INTO last_id
        so.id
        FROM gobs.spatial_object so
        WHERE TRUE
        -- do not modify if there is already a value
        AND so.so_valid_to IS NULL
        -- only for same spatial layer
        AND so.fk_id_spatial_layer = NEW.fk_id_spatial_layer
        -- and same unique id ex: code insee
        AND so.so_unique_id = NEW.so_unique_id
        -- and not for the same object
        AND so.so_uid != NEW.so_uid
        -- only if the new object has a start validity date AFTER the existing one
        AND so.so_valid_from < NEW.so_valid_from
        -- only the preceding one
        ORDER BY so_valid_from DESC
        LIMIT 1
        ;

        -- Update it
        IF last_id > 0 THEN
            UPDATE gobs.spatial_object so
            SET so_valid_to = NEW.so_valid_from
            WHERE so.id = last_id
            ;
        END IF;

    END IF;

    RETURN NEW;
END;
$$;


--
-- PostgreSQL database dump complete
--

