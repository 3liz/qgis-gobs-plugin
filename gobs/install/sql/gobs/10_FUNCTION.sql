--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.17
-- Dumped by pg_dump version 9.6.17

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

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

