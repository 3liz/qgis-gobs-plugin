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

SET default_tablespace = '';

SET default_with_oids = false;

-- actor
CREATE TABLE gobs.actor (
    id integer NOT NULL,
    a_label text NOT NULL,
    a_description text NOT NULL,
    a_email text NOT NULL,
    id_category integer NOT NULL
);


-- actor
COMMENT ON TABLE gobs.actor IS 'Actors';


-- actor_category
CREATE TABLE gobs.actor_category (
    id integer NOT NULL,
    ac_label text NOT NULL,
    ac_description text NOT NULL
);


-- actor_category
COMMENT ON TABLE gobs.actor_category IS 'Actors categories';


-- actor_category_id_seq
CREATE SEQUENCE gobs.actor_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- actor_category_id_seq
ALTER SEQUENCE gobs.actor_category_id_seq OWNED BY gobs.actor_category.id;


-- actor_id_seq
CREATE SEQUENCE gobs.actor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- actor_id_seq
ALTER SEQUENCE gobs.actor_id_seq OWNED BY gobs.actor.id;


-- deleted_data_log
CREATE TABLE gobs.deleted_data_log (
    de_table text NOT NULL,
    de_uid uuid NOT NULL,
    de_timestamp timestamp without time zone DEFAULT now() NOT NULL
);


-- deleted_data_log
COMMENT ON TABLE gobs.deleted_data_log IS 'Log of deleted objects from observation table. Use for synchronization purpose';


-- document
CREATE TABLE gobs.document (
    id integer NOT NULL,
    do_uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    do_label text NOT NULL,
    do_description text,
    do_type text NOT NULL,
    do_path text NOT NULL,
    fk_id_indicator integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


-- document
COMMENT ON TABLE gobs.document IS 'List of documents for describing indicators.';


-- document_id_seq
CREATE SEQUENCE gobs.document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- document_id_seq
ALTER SEQUENCE gobs.document_id_seq OWNED BY gobs.document.id;


-- glossary
CREATE TABLE gobs.glossary (
    id integer NOT NULL,
    gl_field text NOT NULL,
    gl_code text NOT NULL,
    gl_label text NOT NULL,
    gl_description text NOT NULL,
    gl_order smallint
);


-- glossary
COMMENT ON TABLE gobs.glossary IS 'List of labels and words used as labels for stored data';


-- glossary_id_seq
CREATE SEQUENCE gobs.glossary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- glossary_id_seq
ALTER SEQUENCE gobs.glossary_id_seq OWNED BY gobs.glossary.id;


-- graph_node
CREATE TABLE gobs.graph_node (
    id integer NOT NULL,
    gn_label text NOT NULL
);


-- graph_node
COMMENT ON TABLE gobs.graph_node IS 'Graph nodes, to store key words used to find an indicator.';


-- graph_node_id_seq
CREATE SEQUENCE gobs.graph_node_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- graph_node_id_seq
ALTER SEQUENCE gobs.graph_node_id_seq OWNED BY gobs.graph_node.id;


-- import
CREATE TABLE gobs.import (
    id integer NOT NULL,
    im_timestamp timestamp without time zone DEFAULT '2018-06-28 12:15:46.635568'::timestamp without time zone NOT NULL,
    fk_id_series integer NOT NULL,
    im_status text DEFAULT 'p'::text
);


-- import
COMMENT ON TABLE gobs.import IS 'Journal des imports';


-- import_id_seq
CREATE SEQUENCE gobs.import_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- import_id_seq
ALTER SEQUENCE gobs.import_id_seq OWNED BY gobs.import.id;


-- indicator
CREATE TABLE gobs.indicator (
    id integer NOT NULL,
    id_code text NOT NULL,
    id_label text NOT NULL,
    id_description text NOT NULL,
    id_date_format text DEFAULT 'day'::text NOT NULL,
    id_value_code text[] NOT NULL,
    id_value_name text[] NOT NULL,
    id_value_type text[] NOT NULL,
    id_value_unit text[] NOT NULL,
    id_paths text,
    id_category text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


-- indicator
COMMENT ON TABLE gobs.indicator IS 'Groups of observation data for decisional purpose. ';


-- indicator_id_seq
CREATE SEQUENCE gobs.indicator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- indicator_id_seq
ALTER SEQUENCE gobs.indicator_id_seq OWNED BY gobs.indicator.id;


-- metadata
CREATE TABLE gobs.metadata (
    id integer NOT NULL,
    me_version text NOT NULL,
    me_version_date date NOT NULL,
    me_status smallint NOT NULL
);


-- metadata
COMMENT ON TABLE gobs.metadata IS 'Metadata of the structure : version and date. Usefull for database structure and glossary data migrations between versions';


-- metadata_id_seq
CREATE SEQUENCE gobs.metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- metadata_id_seq
ALTER SEQUENCE gobs.metadata_id_seq OWNED BY gobs.metadata.id;


-- observation
CREATE TABLE gobs.observation (
    id bigint NOT NULL,
    fk_id_series integer NOT NULL,
    fk_id_spatial_object bigint NOT NULL,
    fk_id_import integer NOT NULL,
    ob_value jsonb NOT NULL,
    ob_start_timestamp timestamp without time zone NOT NULL,
    ob_validation timestamp without time zone,
    ob_end_timestamp timestamp without time zone,
    ob_uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


-- observation
COMMENT ON TABLE gobs.observation IS 'Les données brutes au format pivot ( indicateur, date, valeurs et entité spatiale, auteur, etc.)';


-- observation_id_seq
CREATE SEQUENCE gobs.observation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- observation_id_seq
ALTER SEQUENCE gobs.observation_id_seq OWNED BY gobs.observation.id;


-- protocol
CREATE TABLE gobs.protocol (
    id integer NOT NULL,
    pr_code text NOT NULL,
    pr_label text NOT NULL,
    pr_description text NOT NULL
);


-- protocol
COMMENT ON TABLE gobs.protocol IS 'List of protocols';


-- protocol_id_seq
CREATE SEQUENCE gobs.protocol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- protocol_id_seq
ALTER SEQUENCE gobs.protocol_id_seq OWNED BY gobs.protocol.id;


-- r_graph_edge
CREATE TABLE gobs.r_graph_edge (
    ge_parent_node integer NOT NULL,
    ge_child_node integer NOT NULL
);


-- r_graph_edge
COMMENT ON TABLE gobs.r_graph_edge IS 'Graph edges: relations between nodes';


-- r_indicator_node
CREATE TABLE gobs.r_indicator_node (
    fk_id_indicator integer NOT NULL,
    fk_id_node integer NOT NULL
);


-- r_indicator_node
COMMENT ON TABLE gobs.r_indicator_node IS 'Pivot table between indicators and nodes';


-- series
CREATE TABLE gobs.series (
    id integer NOT NULL,
    fk_id_protocol integer NOT NULL,
    fk_id_actor integer NOT NULL,
    fk_id_indicator integer NOT NULL,
    fk_id_spatial_layer integer NOT NULL
);


-- series
COMMENT ON TABLE gobs.series IS 'Series of data';


-- series_id_seq
CREATE SEQUENCE gobs.series_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- series_id_seq
ALTER SEQUENCE gobs.series_id_seq OWNED BY gobs.series.id;


-- spatial_layer
CREATE TABLE gobs.spatial_layer (
    id integer NOT NULL,
    sl_code text NOT NULL,
    sl_label text NOT NULL,
    sl_description text NOT NULL,
    sl_creation_date date DEFAULT '2018-06-28'::date NOT NULL,
    fk_id_actor integer NOT NULL,
    sl_geometry_type text NOT NULL
);


-- spatial_layer
COMMENT ON TABLE gobs.spatial_layer IS 'List the spatial layers, used to regroup the spatial data. Ex : cities, rivers, stations';


-- spatial_layer_id_seq
CREATE SEQUENCE gobs.spatial_layer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- spatial_layer_id_seq
ALTER SEQUENCE gobs.spatial_layer_id_seq OWNED BY gobs.spatial_layer.id;


-- spatial_object
CREATE TABLE gobs.spatial_object (
    id bigint NOT NULL,
    so_unique_id text NOT NULL,
    so_unique_label text NOT NULL,
    geom public.geometry(Geometry,4326) NOT NULL,
    fk_id_spatial_layer integer NOT NULL,
    so_valid_from date DEFAULT (now())::date NOT NULL,
    so_valid_to date,
    so_uid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


-- spatial_object
COMMENT ON TABLE gobs.spatial_object IS 'Contains all the spatial objects, caracterized by a geometry type and an entity';


-- spatial_object_id_seq
CREATE SEQUENCE gobs.spatial_object_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- spatial_object_id_seq
ALTER SEQUENCE gobs.spatial_object_id_seq OWNED BY gobs.spatial_object.id;


-- actor id
ALTER TABLE ONLY gobs.actor ALTER COLUMN id SET DEFAULT nextval('gobs.actor_id_seq'::regclass);


-- actor_category id
ALTER TABLE ONLY gobs.actor_category ALTER COLUMN id SET DEFAULT nextval('gobs.actor_category_id_seq'::regclass);


-- document id
ALTER TABLE ONLY gobs.document ALTER COLUMN id SET DEFAULT nextval('gobs.document_id_seq'::regclass);


-- glossary id
ALTER TABLE ONLY gobs.glossary ALTER COLUMN id SET DEFAULT nextval('gobs.glossary_id_seq'::regclass);


-- graph_node id
ALTER TABLE ONLY gobs.graph_node ALTER COLUMN id SET DEFAULT nextval('gobs.graph_node_id_seq'::regclass);


-- import id
ALTER TABLE ONLY gobs.import ALTER COLUMN id SET DEFAULT nextval('gobs.import_id_seq'::regclass);


-- indicator id
ALTER TABLE ONLY gobs.indicator ALTER COLUMN id SET DEFAULT nextval('gobs.indicator_id_seq'::regclass);


-- metadata id
ALTER TABLE ONLY gobs.metadata ALTER COLUMN id SET DEFAULT nextval('gobs.metadata_id_seq'::regclass);


-- observation id
ALTER TABLE ONLY gobs.observation ALTER COLUMN id SET DEFAULT nextval('gobs.observation_id_seq'::regclass);


-- protocol id
ALTER TABLE ONLY gobs.protocol ALTER COLUMN id SET DEFAULT nextval('gobs.protocol_id_seq'::regclass);


-- series id
ALTER TABLE ONLY gobs.series ALTER COLUMN id SET DEFAULT nextval('gobs.series_id_seq'::regclass);


-- spatial_layer id
ALTER TABLE ONLY gobs.spatial_layer ALTER COLUMN id SET DEFAULT nextval('gobs.spatial_layer_id_seq'::regclass);


-- spatial_object id
ALTER TABLE ONLY gobs.spatial_object ALTER COLUMN id SET DEFAULT nextval('gobs.spatial_object_id_seq'::regclass);


--
-- PostgreSQL database dump complete
--

