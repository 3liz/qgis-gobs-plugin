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

SET default_tablespace = '';

SET default_with_oids = false;

-- actor
CREATE TABLE gobs.actor (
    id integer NOT NULL,
    a_name text NOT NULL,
    a_description text NOT NULL,
    a_email text NOT NULL,
    id_category integer NOT NULL
);


-- actor
COMMENT ON TABLE gobs.actor IS 'Actors';


-- actor.id
COMMENT ON COLUMN gobs.actor.id IS 'ID';


-- actor.a_name
COMMENT ON COLUMN gobs.actor.a_name IS 'Name of the actor (can be a person or an entity)';


-- actor.a_description
COMMENT ON COLUMN gobs.actor.a_description IS 'Description of the actor';


-- actor.a_email
COMMENT ON COLUMN gobs.actor.a_email IS 'Email of the actor';


-- actor.id_category
COMMENT ON COLUMN gobs.actor.id_category IS 'Category of actor';


-- actor_category
CREATE TABLE gobs.actor_category (
    id integer NOT NULL,
    ac_name text NOT NULL,
    ac_description text NOT NULL
);


-- actor_category
COMMENT ON TABLE gobs.actor_category IS 'Actors categories';


-- actor_category.id
COMMENT ON COLUMN gobs.actor_category.id IS 'ID';


-- actor_category.ac_name
COMMENT ON COLUMN gobs.actor_category.ac_name IS 'Name of the actor category';


-- actor_category.ac_description
COMMENT ON COLUMN gobs.actor_category.ac_description IS 'Description of the actor category';


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


-- glossary.id
COMMENT ON COLUMN gobs.glossary.id IS 'ID';


-- glossary.gl_field
COMMENT ON COLUMN gobs.glossary.gl_field IS 'Target field for this glossary item';


-- glossary.gl_code
COMMENT ON COLUMN gobs.glossary.gl_code IS 'Item code to store in tables';


-- glossary.gl_label
COMMENT ON COLUMN gobs.glossary.gl_label IS 'Item label to show for users';


-- glossary.gl_description
COMMENT ON COLUMN gobs.glossary.gl_description IS 'Description of the item';


-- glossary.gl_order
COMMENT ON COLUMN gobs.glossary.gl_order IS 'Display order among the field items';


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
    gn_name text NOT NULL,
    gn_description text NOT NULL
);


-- graph_node
COMMENT ON TABLE gobs.graph_node IS 'Graph nodes, to store key words used to find an indicator.';


-- graph_node.id
COMMENT ON COLUMN gobs.graph_node.id IS 'ID';


-- graph_node.gn_name
COMMENT ON COLUMN gobs.graph_node.gn_name IS 'Name of the node';


-- graph_node.gn_description
COMMENT ON COLUMN gobs.graph_node.gn_description IS 'Description of the node';


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


-- import.id
COMMENT ON COLUMN gobs.import.id IS 'Id';


-- import.im_timestamp
COMMENT ON COLUMN gobs.import.im_timestamp IS 'Import date';


-- import.fk_id_series
COMMENT ON COLUMN gobs.import.fk_id_series IS 'Series ID';


-- import.im_status
COMMENT ON COLUMN gobs.import.im_status IS 'Status of import : pending, validated';


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
    id_label text NOT NULL,
    id_title text NOT NULL,
    id_description text NOT NULL,
    id_date_format text DEFAULT 'day'::text NOT NULL,
    id_value_code text[] NOT NULL,
    id_value_name text[] NOT NULL,
    id_value_type text DEFAULT 'integer'::text NOT NULL,
    id_value_unit text NOT NULL,
    id_paths text
);


-- indicator
COMMENT ON TABLE gobs.indicator IS 'Groups of observation data for decisional purpose. ';


-- indicator.id
COMMENT ON COLUMN gobs.indicator.id IS 'ID';


-- indicator.id_label
COMMENT ON COLUMN gobs.indicator.id_label IS 'Short name';


-- indicator.id_title
COMMENT ON COLUMN gobs.indicator.id_title IS 'Title';


-- indicator.id_description
COMMENT ON COLUMN gobs.indicator.id_description IS 'Describes the indicator regarding its rôle inside the project.';


-- indicator.id_date_format
COMMENT ON COLUMN gobs.indicator.id_date_format IS 'Help to know what is the format for the date. Example : ‘year’';


-- indicator.id_value_code
COMMENT ON COLUMN gobs.indicator.id_value_code IS 'List of the codes of the vector dimensions. Ex : [‘pop_h’, ‘pop_f’]';


-- indicator.id_value_name
COMMENT ON COLUMN gobs.indicator.id_value_name IS 'List of the names of the vector dimensions. Ex : [‘population homme’, ‘population femme’]';


-- indicator.id_value_type
COMMENT ON COLUMN gobs.indicator.id_value_type IS 'Type of the stored values. Ex : ‘integer’ or ‘real’';


-- indicator.id_value_unit
COMMENT ON COLUMN gobs.indicator.id_value_unit IS 'Unit ot the store values. Ex : ‘inhabitants’ or ‘°C’';


-- indicator.id_paths
COMMENT ON COLUMN gobs.indicator.id_paths IS 'Paths given to help finding an indicator. They will be split up to fill the graph_node and r_indicator_node tables. If you need multiple paths, use | as a separator. Ex: Environment / Water resources | Measure / Physics / Water';


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


-- metadata.id
COMMENT ON COLUMN gobs.metadata.id IS 'Id of the version';


-- metadata.me_version
COMMENT ON COLUMN gobs.metadata.me_version IS 'Version. Ex: 1.0.2';


-- metadata.me_version_date
COMMENT ON COLUMN gobs.metadata.me_version_date IS 'Date of the version. Ex: 2019-06-01';


-- metadata.me_status
COMMENT ON COLUMN gobs.metadata.me_status IS 'Status of the version. 1 means active version, 0 means older version';


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
    ob_timestamp timestamp without time zone NOT NULL
);


-- observation
COMMENT ON TABLE gobs.observation IS 'Les données brutes au format pivot ( indicateur, date, valeurs et entité spatiale, auteur, etc.)';


-- observation.id
COMMENT ON COLUMN gobs.observation.id IS 'ID';


-- observation.fk_id_series
COMMENT ON COLUMN gobs.observation.fk_id_series IS 'Series ID';


-- observation.fk_id_spatial_object
COMMENT ON COLUMN gobs.observation.fk_id_spatial_object IS 'ID of the object in the spatial object table';


-- observation.fk_id_import
COMMENT ON COLUMN gobs.observation.fk_id_import IS 'Import id';


-- observation.ob_value
COMMENT ON COLUMN gobs.observation.ob_value IS 'Vector containing the measured or computed data values. Ex : [1543, 1637]';


-- observation.ob_timestamp
COMMENT ON COLUMN gobs.observation.ob_timestamp IS 'Timestamp of the data';


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
    pr_name text NOT NULL,
    pr_description text NOT NULL
);


-- protocol
COMMENT ON TABLE gobs.protocol IS 'List of protocols';


-- protocol.id
COMMENT ON COLUMN gobs.protocol.id IS 'ID';


-- protocol.pr_code
COMMENT ON COLUMN gobs.protocol.pr_code IS 'Code';


-- protocol.pr_name
COMMENT ON COLUMN gobs.protocol.pr_name IS 'Name of the indicator';


-- protocol.pr_description
COMMENT ON COLUMN gobs.protocol.pr_description IS 'Description, including URLs to references and authors.';


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


-- r_graph_edge.ge_parent_node
COMMENT ON COLUMN gobs.r_graph_edge.ge_parent_node IS 'Parent node';


-- r_graph_edge.ge_child_node
COMMENT ON COLUMN gobs.r_graph_edge.ge_child_node IS 'Child node';


-- r_indicator_node
CREATE TABLE gobs.r_indicator_node (
    fk_id_indicator integer NOT NULL,
    fk_id_node integer NOT NULL
);


-- r_indicator_node
COMMENT ON TABLE gobs.r_indicator_node IS 'Pivot table between indicators and nodes';


-- r_indicator_node.fk_id_indicator
COMMENT ON COLUMN gobs.r_indicator_node.fk_id_indicator IS 'Parent indicator';


-- r_indicator_node.fk_id_node
COMMENT ON COLUMN gobs.r_indicator_node.fk_id_node IS 'Parent node';


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


-- series.id
COMMENT ON COLUMN gobs.series.id IS 'Id';


-- series.fk_id_protocol
COMMENT ON COLUMN gobs.series.fk_id_protocol IS 'Protocol';


-- series.fk_id_actor
COMMENT ON COLUMN gobs.series.fk_id_actor IS 'Actor, source of the observation data.';


-- series.fk_id_indicator
COMMENT ON COLUMN gobs.series.fk_id_indicator IS 'Indicator. The series is named after the indicator.';


-- series.fk_id_spatial_layer
COMMENT ON COLUMN gobs.series.fk_id_spatial_layer IS 'Spatial layer, mandatory. If needed, use a global spatial layer with only 1 object representing the global area.';


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


-- spatial_layer.sl_code
COMMENT ON COLUMN gobs.spatial_layer.sl_code IS 'Unique short code for the spatial layer';


-- spatial_layer.sl_label
COMMENT ON COLUMN gobs.spatial_layer.sl_label IS 'Label of the spatial layer';


-- spatial_layer.sl_description
COMMENT ON COLUMN gobs.spatial_layer.sl_description IS 'Description';


-- spatial_layer.sl_creation_date
COMMENT ON COLUMN gobs.spatial_layer.sl_creation_date IS 'Creation date';


-- spatial_layer.fk_id_actor
COMMENT ON COLUMN gobs.spatial_layer.fk_id_actor IS 'Source actor.';


-- spatial_layer.sl_geometry_type
COMMENT ON COLUMN gobs.spatial_layer.sl_geometry_type IS 'Type of geometry (POINT, POLYGON, MULTIPOLYGON, etc.)';


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
    fk_id_spatial_layer integer NOT NULL
);


-- spatial_object
COMMENT ON TABLE gobs.spatial_object IS 'Contains all the spatial objects, caracterized by a geometry type and an entity';


-- spatial_object.id
COMMENT ON COLUMN gobs.spatial_object.id IS 'ID';


-- spatial_object.so_unique_id
COMMENT ON COLUMN gobs.spatial_object.so_unique_id IS 'Unique code of each object in the spatial layer ( INSEE, tag, etc.)';


-- spatial_object.so_unique_label
COMMENT ON COLUMN gobs.spatial_object.so_unique_label IS 'Label of each spatial object. Ex : name of the city.';


-- spatial_object.geom
COMMENT ON COLUMN gobs.spatial_object.geom IS 'Geometry of the spatial object. Alway in EPSG:4326';


-- spatial_object.fk_id_spatial_layer
COMMENT ON COLUMN gobs.spatial_object.fk_id_spatial_layer IS 'Spatial layer';


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

