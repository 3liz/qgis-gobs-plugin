
ALTER TABLE gobs.actor RENAME COLUMN a_name TO a_label;
ALTER TABLE gobs.actor_category RENAME COLUMN ac_name TO ac_label;
ALTER TABLE gobs.graph_node RENAME COLUMN gn_name TO gn_label;
ALTER TABLE gobs.indicator RENAME COLUMN id_label TO id_code;
ALTER TABLE gobs.indicator RENAME COLUMN id_title TO id_label;
ALTER TABLE gobs.protocol RENAME COLUMN pr_name TO pr_label;

-- parse_indicator_paths(integer, text)
CREATE OR REPLACE FUNCTION gobs.parse_indicator_paths(i_id integer, i_path text) RETURNS integer
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
