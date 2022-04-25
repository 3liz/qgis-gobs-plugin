--
-- PostgreSQL database dump
--

-- Dumped from database version 13.6 (Ubuntu 13.6-1.pgdg20.04+1+b1)
-- Dumped by pg_dump version 13.6 (Ubuntu 13.6-1.pgdg20.04+1+b1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

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

