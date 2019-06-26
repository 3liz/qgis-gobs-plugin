CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA gobs;

CREATE TABLE gobs.actor (
    id integer NOT NULL,
    a_name text NOT NULL,
    a_description text NOT NULL,
    a_email text NOT NULL,
    id_category integer NOT NULL
);

COMMENT ON TABLE gobs.actor IS 'Actors';
COMMENT ON COLUMN gobs.actor.id IS 'ID';
COMMENT ON COLUMN gobs.actor.a_name IS 'Name of the actor (can be a person or an entity)';
COMMENT ON COLUMN gobs.actor.a_description IS 'Description of the actor';
COMMENT ON COLUMN gobs.actor.a_email IS 'Email of the actor';
COMMENT ON COLUMN gobs.actor.id_category IS 'Category of actor';

CREATE TABLE gobs.actor_category (
    id integer NOT NULL,
    ac_name text NOT NULL,
    ac_description text NOT NULL
);

COMMENT ON TABLE gobs.actor_category IS 'Actors categories';
COMMENT ON COLUMN gobs.actor_category.id IS 'ID';
COMMENT ON COLUMN gobs.actor_category.ac_name IS 'Name of the actor category';
COMMENT ON COLUMN gobs.actor_category.ac_description IS 'Description of the actor category';

CREATE SEQUENCE gobs.actor_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.actor_category_id_seq OWNED BY gobs.actor_category.id;

CREATE SEQUENCE gobs.actor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.actor_id_seq OWNED BY gobs.actor.id;

CREATE TABLE gobs.glossary (
    id integer NOT NULL,
    gl_field text NOT NULL,
    gl_code text NOT NULL,
    gl_label text NOT NULL,
    gl_description text NOT NULL,
    gl_order smallint
);

COMMENT ON TABLE gobs.glossary IS 'List of labels and words used as labels for stored data';
COMMENT ON COLUMN gobs.glossary.id IS 'ID';
COMMENT ON COLUMN gobs.glossary.gl_field IS 'Target field for this glossary item';
COMMENT ON COLUMN gobs.glossary.gl_code IS 'Item code to store in tables';
COMMENT ON COLUMN gobs.glossary.gl_label IS 'Item label to show for users';
COMMENT ON COLUMN gobs.glossary.gl_description IS 'Description of the item';
COMMENT ON COLUMN gobs.glossary.gl_order IS 'Display order among the field items';

CREATE SEQUENCE gobs.glossary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.glossary_id_seq OWNED BY gobs.glossary.id;

CREATE TABLE gobs.graph_node (
    id integer NOT NULL,
    gn_name text NOT NULL,
    gn_description text NOT NULL
);

COMMENT ON TABLE gobs.graph_node IS 'Graph nodes, to store key words used to find an indicator.';
COMMENT ON COLUMN gobs.graph_node.id IS 'ID';
COMMENT ON COLUMN gobs.graph_node.gn_name IS 'Name of the node';
COMMENT ON COLUMN gobs.graph_node.gn_description IS 'Description of the node';

CREATE SEQUENCE gobs.graph_node_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.graph_node_id_seq OWNED BY gobs.graph_node.id;

CREATE TABLE gobs.import (
    id integer NOT NULL,
    im_timestamp timestamp without time zone DEFAULT '2018-06-28 12:15:46.635568'::timestamp without time zone NOT NULL,
    fk_id_series integer NOT NULL,
    im_status text DEFAULT 'p'::text
);

COMMENT ON TABLE gobs.import IS 'Journal des imports';
COMMENT ON COLUMN gobs.import.id IS 'Id';
COMMENT ON COLUMN gobs.import.im_timestamp IS 'Import date';
COMMENT ON COLUMN gobs.import.fk_id_series IS 'Series ID';
COMMENT ON COLUMN gobs.import.im_status IS 'Status of import : pending, validated';

CREATE SEQUENCE gobs.import_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.import_id_seq OWNED BY gobs.import.id;

CREATE TABLE gobs.indicator (
    id integer NOT NULL,
    id_label text NOT NULL,
    id_title text NOT NULL,
    id_description text NOT NULL,
    id_date_format text DEFAULT 'day'::text NOT NULL,
    id_value_code text[] NOT NULL,
    id_value_name text[] NOT NULL,
    id_value_type text DEFAULT 'integer'::text NOT NULL,
    id_value_unit text NOT NULL
);

COMMENT ON TABLE gobs.indicator IS 'Groups of observation data for decisional purpose. ';
COMMENT ON COLUMN gobs.indicator.id IS 'ID';
COMMENT ON COLUMN gobs.indicator.id_label IS 'Short name';
COMMENT ON COLUMN gobs.indicator.id_title IS 'Title';
COMMENT ON COLUMN gobs.indicator.id_description IS 'Describes the indicator regarding its rôle inside the project.';
COMMENT ON COLUMN gobs.indicator.id_date_format IS 'Help to know what is the format for the date. Example : ‘year’';
COMMENT ON COLUMN gobs.indicator.id_value_code IS 'List of the codes of the vector dimensions. Ex : [‘pop_h’, ‘pop_f’]';
COMMENT ON COLUMN gobs.indicator.id_value_name IS 'List of the names of the vector dimensions. Ex : [‘population homme’, ‘population femme’]';
COMMENT ON COLUMN gobs.indicator.id_value_type IS 'Type of the stored values. Ex : ‘integer’ or ‘real’';
COMMENT ON COLUMN gobs.indicator.id_value_unit IS 'Unit ot the store values. Ex : ‘inhabitants’ or ‘°C’';

CREATE SEQUENCE gobs.indicator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.indicator_id_seq OWNED BY gobs.indicator.id;

CREATE TABLE gobs.observation (
    id bigint NOT NULL,
    fk_id_series integer NOT NULL,
    fk_id_spatial_object bigint NOT NULL,
    fk_id_import integer NOT NULL,
    ob_value jsonb NOT NULL,
    ob_timestamp timestamp without time zone NOT NULL
);

COMMENT ON TABLE gobs.observation IS 'Les données brutes au format pivot ( indicateur, date, valeurs et entité spatiale, auteur, etc.)';
COMMENT ON COLUMN gobs.observation.id IS 'ID';
COMMENT ON COLUMN gobs.observation.fk_id_series IS 'Series ID';
COMMENT ON COLUMN gobs.observation.fk_id_spatial_object IS 'ID of the object in the spatial object table';
COMMENT ON COLUMN gobs.observation.fk_id_import IS 'Import id';
COMMENT ON COLUMN gobs.observation.ob_value IS 'Vector containing the measured or computed data values. Ex : [1543, 1637]';
COMMENT ON COLUMN gobs.observation.ob_timestamp IS 'Timestamp of the data';

CREATE SEQUENCE gobs.observation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.observation_id_seq OWNED BY gobs.observation.id;

CREATE TABLE gobs.protocol (
    id integer NOT NULL,
    pr_code text NOT NULL,
    pr_name text NOT NULL,
    pr_description text NOT NULL
);

COMMENT ON TABLE gobs.protocol IS 'List of protocols';
COMMENT ON COLUMN gobs.protocol.id IS 'ID';
COMMENT ON COLUMN gobs.protocol.pr_code IS 'Code';
COMMENT ON COLUMN gobs.protocol.pr_name IS 'Name of the indicator';
COMMENT ON COLUMN gobs.protocol.pr_description IS 'Description, including URLs to references and authors.';

CREATE SEQUENCE gobs.protocol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.protocol_id_seq OWNED BY gobs.protocol.id;

CREATE TABLE gobs.r_graph_edge (
    ge_parent_node integer NOT NULL,
    ge_child_node integer NOT NULL
);

COMMENT ON TABLE gobs.r_graph_edge IS 'Graph edges: relations between nodes';
COMMENT ON COLUMN gobs.r_graph_edge.ge_parent_node IS 'Parent node';
COMMENT ON COLUMN gobs.r_graph_edge.ge_child_node IS 'Child node';

CREATE TABLE gobs.r_indicator_node (
    fk_id_indicator integer NOT NULL,
    fk_id_node integer NOT NULL
);

COMMENT ON TABLE gobs.r_indicator_node IS 'Pivot table between indicators and nodes';
COMMENT ON COLUMN gobs.r_indicator_node.fk_id_indicator IS 'Parent indicator';
COMMENT ON COLUMN gobs.r_indicator_node.fk_id_node IS 'Parent node';

CREATE TABLE gobs.series (
    id integer NOT NULL,
    fk_id_protocol integer NOT NULL,
    fk_id_actor integer NOT NULL,
    fk_id_indicator integer NOT NULL,
    fk_id_spatial_layer integer NOT NULL
);

COMMENT ON TABLE gobs.series IS 'Series of data';
COMMENT ON COLUMN gobs.series.id IS 'Id';
COMMENT ON COLUMN gobs.series.fk_id_protocol IS 'Protocol';
COMMENT ON COLUMN gobs.series.fk_id_actor IS 'Actor, source of the observation data.';
COMMENT ON COLUMN gobs.series.fk_id_indicator IS 'Indicator. The series is named after the indicator.';
COMMENT ON COLUMN gobs.series.fk_id_spatial_layer IS 'Spatial layer, mandatory. If needed, use a global spatial layer with only 1 object representing the global area.';

CREATE SEQUENCE gobs.series_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.series_id_seq OWNED BY gobs.series.id;

CREATE TABLE gobs.spatial_layer (
    id integer NOT NULL,
    sl_code text NOT NULL,
    sl_label text NOT NULL,
    sl_description text NOT NULL,
    sl_creation_date date DEFAULT '2018-06-28'::date NOT NULL,
    fk_id_actor integer NOT NULL,
    sl_geometry_type text NOT NULL
);

COMMENT ON TABLE gobs.spatial_layer IS 'List the spatial layers, used to regroup the spatial data. Ex : cities, rivers, stations';
COMMENT ON COLUMN gobs.spatial_layer.sl_code IS 'Unique short code for the spatial layer';
COMMENT ON COLUMN gobs.spatial_layer.sl_label IS 'Label of the spatial layer';
COMMENT ON COLUMN gobs.spatial_layer.sl_description IS 'Description';
COMMENT ON COLUMN gobs.spatial_layer.sl_creation_date IS 'Creation date';
COMMENT ON COLUMN gobs.spatial_layer.fk_id_actor IS 'Source actor.';
COMMENT ON COLUMN gobs.spatial_layer.sl_geometry_type IS 'Type of geometry (POINT, POLYGON, MULTIPOLYGON, etc.)';

CREATE SEQUENCE gobs.spatial_layer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.spatial_layer_id_seq OWNED BY gobs.spatial_layer.id;

CREATE TABLE gobs.spatial_object (
    id bigint NOT NULL,
    so_unique_id text NOT NULL,
    so_unique_label text NOT NULL,
    geom public.geometry(Geometry,4326) NOT NULL,
    fk_id_spatial_layer integer NOT NULL
);

COMMENT ON TABLE gobs.spatial_object IS 'Contains all the spatial objects, caracterized by a geometry type and an entity';
COMMENT ON COLUMN gobs.spatial_object.id IS 'ID';
COMMENT ON COLUMN gobs.spatial_object.so_unique_id IS 'Unique code of each object in the spatial layer ( INSEE, tag, etc.)';
COMMENT ON COLUMN gobs.spatial_object.so_unique_label IS 'Label of each spatial object. Ex : name of the city.';
COMMENT ON COLUMN gobs.spatial_object.geom IS 'Geometry of the spatial object. Alway in EPSG:4326';
COMMENT ON COLUMN gobs.spatial_object.fk_id_spatial_layer IS 'Spatial layer';

CREATE SEQUENCE gobs.spatial_object_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE gobs.spatial_object_id_seq OWNED BY gobs.spatial_object.id;

ALTER TABLE ONLY gobs.actor ALTER COLUMN id SET DEFAULT nextval('gobs.actor_id_seq'::regclass);

ALTER TABLE ONLY gobs.actor_category ALTER COLUMN id SET DEFAULT nextval('gobs.actor_category_id_seq'::regclass);

ALTER TABLE ONLY gobs.glossary ALTER COLUMN id SET DEFAULT nextval('gobs.glossary_id_seq'::regclass);

ALTER TABLE ONLY gobs.graph_node ALTER COLUMN id SET DEFAULT nextval('gobs.graph_node_id_seq'::regclass);

ALTER TABLE ONLY gobs.import ALTER COLUMN id SET DEFAULT nextval('gobs.import_id_seq'::regclass);

ALTER TABLE ONLY gobs.indicator ALTER COLUMN id SET DEFAULT nextval('gobs.indicator_id_seq'::regclass);

ALTER TABLE ONLY gobs.observation ALTER COLUMN id SET DEFAULT nextval('gobs.observation_id_seq'::regclass);

ALTER TABLE ONLY gobs.protocol ALTER COLUMN id SET DEFAULT nextval('gobs.protocol_id_seq'::regclass);

ALTER TABLE ONLY gobs.series ALTER COLUMN id SET DEFAULT nextval('gobs.series_id_seq'::regclass);

ALTER TABLE ONLY gobs.spatial_layer ALTER COLUMN id SET DEFAULT nextval('gobs.spatial_layer_id_seq'::regclass);

ALTER TABLE ONLY gobs.spatial_object ALTER COLUMN id SET DEFAULT nextval('gobs.spatial_object_id_seq'::regclass);

ALTER TABLE ONLY gobs.actor_category
    ADD CONSTRAINT actor_category_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.glossary
    ADD CONSTRAINT glossary_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.graph_node
    ADD CONSTRAINT graph_node_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.import
    ADD CONSTRAINT import_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.indicator
    ADD CONSTRAINT indicator_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.protocol
    ADD CONSTRAINT protocol_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.r_graph_edge
    ADD CONSTRAINT r_graph_edge_pkey PRIMARY KEY (ge_parent_node, ge_child_node);

ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_pkey PRIMARY KEY (fk_id_indicator, fk_id_node);

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.spatial_layer
    ADD CONSTRAINT spatial_layer_pkey PRIMARY KEY (id);

ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_pkey PRIMARY KEY (id);

CREATE INDEX actor_a_name_idx ON gobs.actor USING btree (a_name);

CREATE INDEX glossary_gl_field_idx ON gobs.glossary USING btree (gl_field);

CREATE INDEX graph_node_gn_name_idx ON gobs.graph_node USING btree (gn_name);

CREATE INDEX import_fk_id_series_idx ON gobs.import USING btree (fk_id_series);

CREATE INDEX indicator_id_label_idx ON gobs.indicator USING btree (id_label);

CREATE INDEX observation_fk_id_import_idx ON gobs.observation USING btree (fk_id_import);

CREATE INDEX observation_fk_id_series_idx ON gobs.observation USING btree (fk_id_series);

CREATE INDEX observation_fk_id_spatial_object_idx ON gobs.observation USING btree (fk_id_spatial_object);

CREATE INDEX observation_ob_timestamp_idx ON gobs.observation USING btree (ob_timestamp);

CREATE INDEX protocol_pr_code_idx ON gobs.protocol USING btree (pr_code);

CREATE INDEX series_fk_id_actor_idx ON gobs.series USING btree (fk_id_actor);

CREATE INDEX series_fk_id_indicator_idx ON gobs.series USING btree (fk_id_indicator);

CREATE INDEX series_fk_id_protocol_idx ON gobs.series USING btree (fk_id_protocol);

CREATE INDEX series_fk_id_spatial_layer_idx ON gobs.series USING btree (fk_id_spatial_layer);

CREATE INDEX spatial_layer_sl_code_idx ON gobs.spatial_layer USING btree (sl_code);

CREATE INDEX spatial_object_fk_id_spatial_layer_idx ON gobs.spatial_object USING btree (fk_id_spatial_layer);

CREATE INDEX spatial_object_geom_idx ON gobs.spatial_object USING btree (geom);

ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_id_category_fkey FOREIGN KEY (id_category) REFERENCES gobs.actor_category(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.import
    ADD CONSTRAINT import_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_import_fkey FOREIGN KEY (fk_id_import) REFERENCES gobs.import(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_spatial_object_fkey FOREIGN KEY (fk_id_spatial_object) REFERENCES gobs.spatial_object(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE CASCADE;

ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_node_fkey FOREIGN KEY (fk_id_node) REFERENCES gobs.graph_node(id) ON DELETE CASCADE;

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_protocol_fkey FOREIGN KEY (fk_id_protocol) REFERENCES gobs.protocol(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.spatial_layer
    ADD CONSTRAINT spatial_layer_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;

ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;

