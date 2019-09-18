--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.15
-- Dumped by pg_dump version 9.6.15

SET statement_timeout = 0;
SET lock_timeout = 0;
-- SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- actor_category actor_category_pkey
ALTER TABLE ONLY gobs.actor_category
    ADD CONSTRAINT actor_category_pkey PRIMARY KEY (id);


-- actor actor_pkey
ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_pkey PRIMARY KEY (id);


-- glossary glossary_pkey
ALTER TABLE ONLY gobs.glossary
    ADD CONSTRAINT glossary_pkey PRIMARY KEY (id);


-- graph_node graph_node_pkey
ALTER TABLE ONLY gobs.graph_node
    ADD CONSTRAINT graph_node_pkey PRIMARY KEY (id);


-- import import_pkey
ALTER TABLE ONLY gobs.import
    ADD CONSTRAINT import_pkey PRIMARY KEY (id);


-- indicator indicator_pkey
ALTER TABLE ONLY gobs.indicator
    ADD CONSTRAINT indicator_pkey PRIMARY KEY (id);


-- metadata metadata_me_version_key
ALTER TABLE ONLY gobs.metadata
    ADD CONSTRAINT metadata_me_version_key UNIQUE (me_version);


-- metadata metadata_pkey
ALTER TABLE ONLY gobs.metadata
    ADD CONSTRAINT metadata_pkey PRIMARY KEY (id);


-- observation observation_pkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_pkey PRIMARY KEY (id);


-- protocol protocol_pkey
ALTER TABLE ONLY gobs.protocol
    ADD CONSTRAINT protocol_pkey PRIMARY KEY (id);


-- qgisproject qgisproject_pkey
ALTER TABLE ONLY gobs.qgisproject
    ADD CONSTRAINT qgisproject_pkey PRIMARY KEY (id);


-- qgisproject qgisproject_qp_project_qp_repository_key
ALTER TABLE ONLY gobs.qgisproject
    ADD CONSTRAINT qgisproject_qp_project_qp_repository_key UNIQUE (qp_project, qp_repository);


-- r_graph_edge r_graph_edge_pkey
ALTER TABLE ONLY gobs.r_graph_edge
    ADD CONSTRAINT r_graph_edge_pkey PRIMARY KEY (ge_parent_node, ge_child_node);


-- r_indicator_node r_indicator_node_pkey
ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_pkey PRIMARY KEY (fk_id_indicator, fk_id_node);


-- r_qgisproject_node r_qgisproject_node_pkey
ALTER TABLE ONLY gobs.r_qgisproject_node
    ADD CONSTRAINT r_qgisproject_node_pkey PRIMARY KEY (fk_id_qgisproject, fk_id_node);


-- series series_pkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_pkey PRIMARY KEY (id);


-- spatial_layer spatial_layer_pkey
ALTER TABLE ONLY gobs.spatial_layer
    ADD CONSTRAINT spatial_layer_pkey PRIMARY KEY (id);


-- spatial_object spatial_object_pkey
ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_pkey PRIMARY KEY (id);


-- spatial_object spatial_object_so_unique_id_fk_id_spatial_layer_key
ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_so_unique_id_fk_id_spatial_layer_key UNIQUE (so_unique_id, fk_id_spatial_layer);


-- actor actor_id_category_fkey
ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_id_category_fkey FOREIGN KEY (id_category) REFERENCES gobs.actor_category(id) ON DELETE RESTRICT;


-- import import_fk_id_series_fkey
ALTER TABLE ONLY gobs.import
    ADD CONSTRAINT import_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;


-- observation observation_fk_id_import_fkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_import_fkey FOREIGN KEY (fk_id_import) REFERENCES gobs.import(id) ON DELETE RESTRICT;


-- observation observation_fk_id_series_fkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;


-- observation observation_fk_id_spatial_object_fkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_spatial_object_fkey FOREIGN KEY (fk_id_spatial_object) REFERENCES gobs.spatial_object(id) ON DELETE RESTRICT;


-- r_indicator_node r_indicator_node_fk_id_indicator_fkey
ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE CASCADE;


-- r_indicator_node r_indicator_node_fk_id_node_fkey
ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_node_fkey FOREIGN KEY (fk_id_node) REFERENCES gobs.graph_node(id) ON DELETE CASCADE;


-- r_qgisproject_node r_qgisproject_node_fk_id_node_fkey
ALTER TABLE ONLY gobs.r_qgisproject_node
    ADD CONSTRAINT r_qgisproject_node_fk_id_node_fkey FOREIGN KEY (fk_id_node) REFERENCES gobs.graph_node(id) ON DELETE CASCADE;


-- r_qgisproject_node r_qgisproject_node_fk_id_qgisproject_fkey
ALTER TABLE ONLY gobs.r_qgisproject_node
    ADD CONSTRAINT r_qgisproject_node_fk_id_qgisproject_fkey FOREIGN KEY (fk_id_qgisproject) REFERENCES gobs.qgisproject(id) ON DELETE CASCADE;


-- series series_fk_id_actor_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;


-- series series_fk_id_indicator_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE RESTRICT;


-- series series_fk_id_protocol_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_protocol_fkey FOREIGN KEY (fk_id_protocol) REFERENCES gobs.protocol(id) ON DELETE RESTRICT;


-- series series_fk_id_spatial_layer_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;


-- spatial_layer spatial_layer_fk_id_actor_fkey
ALTER TABLE ONLY gobs.spatial_layer
    ADD CONSTRAINT spatial_layer_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;


-- spatial_object spatial_object_fk_id_spatial_layer_fkey
ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

