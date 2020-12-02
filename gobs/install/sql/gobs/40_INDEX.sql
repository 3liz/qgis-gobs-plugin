--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.17
-- Dumped by pg_dump version 9.6.17

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

-- actor_a_name_idx
CREATE INDEX actor_a_name_idx ON gobs.actor USING btree (a_label);


-- glossary_gl_field_idx
CREATE INDEX glossary_gl_field_idx ON gobs.glossary USING btree (gl_field);


-- graph_node_gn_name_idx
CREATE INDEX graph_node_gn_name_idx ON gobs.graph_node USING btree (gn_label);


-- import_fk_id_series_idx
CREATE INDEX import_fk_id_series_idx ON gobs.import USING btree (fk_id_series);


-- indicator_id_label_idx
CREATE INDEX indicator_id_label_idx ON gobs.indicator USING btree (id_code);


-- observation_fk_id_import_idx
CREATE INDEX observation_fk_id_import_idx ON gobs.observation USING btree (fk_id_import);


-- observation_fk_id_series_idx
CREATE INDEX observation_fk_id_series_idx ON gobs.observation USING btree (fk_id_series);


-- observation_fk_id_spatial_object_idx
CREATE INDEX observation_fk_id_spatial_object_idx ON gobs.observation USING btree (fk_id_spatial_object);


-- observation_ob_timestamp_idx
CREATE INDEX observation_ob_timestamp_idx ON gobs.observation USING btree (ob_start_timestamp);


-- protocol_pr_code_idx
CREATE INDEX protocol_pr_code_idx ON gobs.protocol USING btree (pr_code);


-- series_fk_id_actor_idx
CREATE INDEX series_fk_id_actor_idx ON gobs.series USING btree (fk_id_actor);


-- series_fk_id_indicator_idx
CREATE INDEX series_fk_id_indicator_idx ON gobs.series USING btree (fk_id_indicator);


-- series_fk_id_protocol_idx
CREATE INDEX series_fk_id_protocol_idx ON gobs.series USING btree (fk_id_protocol);


-- series_fk_id_spatial_layer_idx
CREATE INDEX series_fk_id_spatial_layer_idx ON gobs.series USING btree (fk_id_spatial_layer);


-- spatial_layer_sl_code_idx
CREATE INDEX spatial_layer_sl_code_idx ON gobs.spatial_layer USING btree (sl_code);


-- spatial_object_fk_id_spatial_layer_idx
CREATE INDEX spatial_object_fk_id_spatial_layer_idx ON gobs.spatial_object USING btree (fk_id_spatial_layer);


-- spatial_object_geom_idx
CREATE INDEX spatial_object_geom_idx ON gobs.spatial_object USING gist (geom);


--
-- PostgreSQL database dump complete
--

