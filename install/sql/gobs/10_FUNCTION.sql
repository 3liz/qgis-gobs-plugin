--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.16
-- Dumped by pg_dump version 9.6.16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- parse_indicator_paths(integer, text)
CREATE FUNCTION gobs.parse_indicator_paths(i_id integer, i_path text) RETURNS integer
    LANGUAGE plpgsql
    AS $$ DECLARE 	_path text; 	_group text; 	_word text; 	_parent text; 	_gid integer; 	_leaf text; 	_leaves text[]; BEGIN 	_parent = NULL;  	INSERT INTO gobs.graph_node (gn_name) 	VALUES ('ROOT') 	ON CONFLICT DO NOTHING; 	 	FOR _group IN  		SELECT trim(g) 		FROM regexp_split_to_table(i_path, ',') AS g	 	LOOP 		RAISE NOTICE 'groupe = "%" ', _group; 		FOR _word IN  			SELECT trim(w) AS w 			FROM regexp_split_to_table(_group, '/') AS w 		LOOP 			RAISE NOTICE '  * word = "%", parent = "%" ', _word, _parent; 			 			INSERT INTO gobs.graph_node (gn_name) 			VALUES (_word) 			ON CONFLICT (gn_name) 			DO NOTHING 			RETURNING id 			INTO _gid; 			IF _gid IS NULL THEN 				SELECT id INTO _gid  				FROM gobs.graph_node 				WHERE gn_name = _word; 			END IF; 			 			INSERT INTO gobs.r_graph_edge (ge_parent_node, ge_child_node) 			VALUES ( 				(SELECT id FROM gobs.graph_node WHERE gn_name = coalesce(_parent, 'ROOT') LIMIT 1), 				_gid 			) 			ON CONFLICT DO NOTHING; 			 			_parent =  _word; 			 			_leaf = _word; 			 		END LOOP;		 		_parent =  NULL; 		 		_leaves = _leaves || _leaf ; 		_leaf = NULL; 	END LOOP; 	 	RAISE NOTICE '  leaves % ', _leaves;  	INSERT INTO gobs.r_indicator_node  	(fk_id_indicator, fk_id_node) 	SELECT i_id, ( 		SELECT id FROM gobs.graph_node WHERE gn_name = leaf LIMIT 1 	) 	FROM ( 		SELECT unnest(_leaves) AS leaf 	) AS source 	ON CONFLICT DO NOTHING; 	 	RETURN 1; END; $$;


-- trg_parse_indicator_paths()
CREATE FUNCTION gobs.trg_parse_indicator_paths() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ DECLARE     _output integer; BEGIN 	IF TG_OP = 'INSERT' OR NEW.id_paths != OLD.id_paths THEN 		SELECT gobs.parse_indicator_paths(NEW.id, NEW.id_paths)  		INTO _output; 	END IF; 	 	RETURN NEW; END; $$;


--
-- PostgreSQL database dump complete
--

