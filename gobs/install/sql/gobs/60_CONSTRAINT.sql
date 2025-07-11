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

SET default_tablespace = '';

-- actor actor_a_login_key
ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_a_login_key UNIQUE (a_login);


-- actor_category actor_category_ac_label_key
ALTER TABLE ONLY gobs.actor_category
    ADD CONSTRAINT actor_category_ac_label_key UNIQUE (ac_label);


-- actor_category actor_category_pkey
ALTER TABLE ONLY gobs.actor_category
    ADD CONSTRAINT actor_category_pkey PRIMARY KEY (id);


-- actor actor_pkey
ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_pkey PRIMARY KEY (id);


-- deleted_data_log deleted_data_log_pkey
ALTER TABLE ONLY gobs.deleted_data_log
    ADD CONSTRAINT deleted_data_log_pkey PRIMARY KEY (de_table, de_uid);


-- dimension dimension_fk_id_indicator_di_code_key
ALTER TABLE ONLY gobs.dimension
    ADD CONSTRAINT dimension_fk_id_indicator_di_code_key UNIQUE (fk_id_indicator, di_code);


-- dimension dimension_pkey
ALTER TABLE ONLY gobs.dimension
    ADD CONSTRAINT dimension_pkey PRIMARY KEY (id);


-- document document_do_label_key
ALTER TABLE ONLY gobs.document
    ADD CONSTRAINT document_do_label_key UNIQUE (do_label, fk_id_indicator);


-- document document_pkey
ALTER TABLE ONLY gobs.document
    ADD CONSTRAINT document_pkey PRIMARY KEY (id);


-- glossary glossary_pkey
ALTER TABLE ONLY gobs.glossary
    ADD CONSTRAINT glossary_pkey PRIMARY KEY (id);


-- graph_node graph_node_gn_name_unique
ALTER TABLE ONLY gobs.graph_node
    ADD CONSTRAINT graph_node_gn_name_unique UNIQUE (gn_label);


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


-- observation observation_data_unique
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_data_unique UNIQUE (fk_id_series, fk_id_spatial_object, ob_start_timestamp);


-- observation observation_pkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_pkey PRIMARY KEY (id);


-- project project_pkey
ALTER TABLE ONLY gobs.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


-- project project_pt_code_key
ALTER TABLE ONLY gobs.project
    ADD CONSTRAINT project_pt_code_key UNIQUE (pt_code);


-- project project_pt_label_key
ALTER TABLE ONLY gobs.project
    ADD CONSTRAINT project_pt_label_key UNIQUE (pt_label);


-- project_view project_view_pkey
ALTER TABLE ONLY gobs.project_view
    ADD CONSTRAINT project_view_pkey PRIMARY KEY (id);


-- protocol protocol_pkey
ALTER TABLE ONLY gobs.protocol
    ADD CONSTRAINT protocol_pkey PRIMARY KEY (id);


-- r_graph_edge r_graph_edge_pkey
ALTER TABLE ONLY gobs.r_graph_edge
    ADD CONSTRAINT r_graph_edge_pkey PRIMARY KEY (ge_parent_node, ge_child_node);


-- r_indicator_node r_indicator_node_pkey
ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_pkey PRIMARY KEY (fk_id_indicator, fk_id_node);


-- series series_pkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_pkey PRIMARY KEY (id);


-- spatial_layer spatial_layer_pkey
ALTER TABLE ONLY gobs.spatial_layer
    ADD CONSTRAINT spatial_layer_pkey PRIMARY KEY (id);


-- spatial_object spatial_object_pkey
ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_pkey PRIMARY KEY (id);


-- spatial_object spatial_object_unique_key
ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_unique_key UNIQUE (so_unique_id, fk_id_spatial_layer, so_valid_from);


-- actor actor_id_category_fkey
ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_id_category_fkey FOREIGN KEY (id_category) REFERENCES gobs.actor_category(id) ON DELETE RESTRICT;


-- dimension dimension_fk_id_indicator_fkey
ALTER TABLE ONLY gobs.dimension
    ADD CONSTRAINT dimension_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id);


-- document document_fk_id_indicator_fkey
ALTER TABLE ONLY gobs.document
    ADD CONSTRAINT document_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id);


-- import import_fk_id_series_fkey
ALTER TABLE ONLY gobs.import
    ADD CONSTRAINT import_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;


-- observation observation_fk_id_actor_fkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;


-- observation observation_fk_id_import_fkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_import_fkey FOREIGN KEY (fk_id_import) REFERENCES gobs.import(id) ON DELETE RESTRICT;


-- observation observation_fk_id_series_fkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;


-- observation observation_fk_id_spatial_object_fkey
ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_spatial_object_fkey FOREIGN KEY (fk_id_spatial_object) REFERENCES gobs.spatial_object(id) ON DELETE RESTRICT;


-- project_view project_view_fk_id_project_fkey
ALTER TABLE ONLY gobs.project_view
    ADD CONSTRAINT project_view_fk_id_project_fkey FOREIGN KEY (fk_id_project) REFERENCES gobs.project(id) ON DELETE CASCADE;


-- r_indicator_node r_indicator_node_fk_id_indicator_fkey
ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE CASCADE;


-- r_indicator_node r_indicator_node_fk_id_node_fkey
ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_node_fkey FOREIGN KEY (fk_id_node) REFERENCES gobs.graph_node(id) ON DELETE CASCADE;


-- series series_fk_id_indicator_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE RESTRICT;


-- series series_fk_id_project_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_project_fkey FOREIGN KEY (fk_id_project) REFERENCES gobs.project(id) ON DELETE RESTRICT;


-- series series_fk_id_protocol_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_protocol_fkey FOREIGN KEY (fk_id_protocol) REFERENCES gobs.protocol(id) ON DELETE RESTRICT;


-- series series_fk_id_spatial_layer_fkey
ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;


-- spatial_object spatial_object_fk_id_actor_fkey
ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;


-- spatial_object spatial_object_fk_id_spatial_layer_fkey
ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

