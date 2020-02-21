-- graph_node
ALTER TABLE gobs.graph_node DROP CONSTRAINT IF EXISTS graph_node_gn_name_unique ;
ALTER TABLE gobs.graph_node ADD CONSTRAINT graph_node_gn_name_unique UNIQUE (gn_name);

ALTER TABLE gobs.graph_node DROP COLUMN IF EXISTS gn_description;

-- Indicator path parser
CREATE OR REPLACE FUNCTION gobs.parse_indicator_paths(i_id integer, i_path text)
RETURNS INTEGER
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
    INSERT INTO gobs.graph_node (gn_name)
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
            INSERT INTO gobs.graph_node (gn_name)
            VALUES (_word)
            ON CONFLICT (gn_name)
            DO NOTHING
            RETURNING id
            INTO _gid;
            IF _gid IS NULL THEN
                SELECT id INTO _gid
                FROM gobs.graph_node
                WHERE gn_name = _word;
            END IF;

            -- gobs.r_graph_edge
            INSERT INTO gobs.r_graph_edge (ge_parent_node, ge_child_node)
            VALUES (
                (SELECT id FROM gobs.graph_node WHERE gn_name = coalesce(_parent, 'ROOT') LIMIT 1),
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
        SELECT id FROM gobs.graph_node WHERE gn_name = leaf LIMIT 1
    )
    FROM (
        SELECT unnest(_leaves) AS leaf
    ) AS source
    ON CONFLICT DO NOTHING;

    RETURN 1;
END;
$$
;
CREATE OR REPLACE FUNCTION gobs.trg_parse_indicator_paths()
RETURNS TRIGGER
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
$$
;
DROP TRIGGER IF EXISTS gobs_on_indicator_change
ON gobs.indicator;
CREATE TRIGGER gobs_on_indicator_change
AFTER INSERT OR UPDATE ON gobs.indicator
FOR EACH ROW EXECUTE PROCEDURE gobs.trg_parse_indicator_paths();

-- RUN
TRUNCATE gobs.r_graph_edge RESTART IDENTITY CASCADE;
TRUNCATE gobs.graph_node RESTART IDENTITY CASCADE;
TRUNCATE gobs.r_indicator_node RESTART IDENTITY CASCADE;
UPDATE gobs.indicator SET id_paths = id_paths || ' ';
