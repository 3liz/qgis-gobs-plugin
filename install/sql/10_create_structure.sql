CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA gobs;


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: actor; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.actor (
    id integer NOT NULL,
    a_name text NOT NULL,
    a_description text NOT NULL,
    a_email text NOT NULL,
    id_category integer NOT NULL
);


--
-- Name: TABLE actor; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.actor IS 'Actors';


--
-- Name: COLUMN actor.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor.id IS 'ID';


--
-- Name: COLUMN actor.a_name; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor.a_name IS 'Name of the actor (can be a person or an entity)';


--
-- Name: COLUMN actor.a_description; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor.a_description IS 'Description of the actor';


--
-- Name: COLUMN actor.a_email; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor.a_email IS 'Email of the actor';


--
-- Name: COLUMN actor.id_category; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor.id_category IS 'Category of actor';


--
-- Name: actor_category; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.actor_category (
    id integer NOT NULL,
    ac_name text NOT NULL,
    ac_description text NOT NULL
);


--
-- Name: TABLE actor_category; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.actor_category IS 'Actors categories';


--
-- Name: COLUMN actor_category.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor_category.id IS 'ID';


--
-- Name: COLUMN actor_category.ac_name; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor_category.ac_name IS 'Name of the actor category';


--
-- Name: COLUMN actor_category.ac_description; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.actor_category.ac_description IS 'Description of the actor category';


--
-- Name: actor_category_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.actor_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: actor_category_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.actor_category_id_seq OWNED BY gobs.actor_category.id;


--
-- Name: actor_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.actor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: actor_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.actor_id_seq OWNED BY gobs.actor.id;


--
-- Name: glossary; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.glossary (
    id integer NOT NULL,
    gl_field text NOT NULL,
    gl_code text NOT NULL,
    gl_label text NOT NULL,
    gl_description text NOT NULL,
    gl_order smallint
);


--
-- Name: TABLE glossary; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.glossary IS 'List of labels and words used as labels for stored data';


--
-- Name: COLUMN glossary.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.glossary.id IS 'ID';


--
-- Name: COLUMN glossary.gl_field; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.glossary.gl_field IS 'Target field for this glossary item';


--
-- Name: COLUMN glossary.gl_code; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.glossary.gl_code IS 'Item code to store in tables';


--
-- Name: COLUMN glossary.gl_label; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.glossary.gl_label IS 'Item label to show for users';


--
-- Name: COLUMN glossary.gl_description; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.glossary.gl_description IS 'Description of the item';


--
-- Name: COLUMN glossary.gl_order; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.glossary.gl_order IS 'Display order among the field items';


--
-- Name: glossary_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.glossary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: glossary_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.glossary_id_seq OWNED BY gobs.glossary.id;


--
-- Name: graph_node; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.graph_node (
    id integer NOT NULL,
    gn_name text NOT NULL,
    gn_description text NOT NULL
);


--
-- Name: TABLE graph_node; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.graph_node IS 'Graph nodes, to store key words used to find an indicator.';


--
-- Name: COLUMN graph_node.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.graph_node.id IS 'ID';


--
-- Name: COLUMN graph_node.gn_name; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.graph_node.gn_name IS 'Name of the node';


--
-- Name: COLUMN graph_node.gn_description; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.graph_node.gn_description IS 'Description of the node';


--
-- Name: graph_node_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.graph_node_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: graph_node_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.graph_node_id_seq OWNED BY gobs.graph_node.id;


--
-- Name: import; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.import (
    id integer NOT NULL,
    im_timestamp timestamp without time zone DEFAULT '2018-06-28 12:15:46.635568'::timestamp without time zone NOT NULL,
    fk_id_series integer NOT NULL,
    im_status text DEFAULT 'p'::text
);


--
-- Name: TABLE import; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.import IS 'Journal des imports';


--
-- Name: COLUMN import.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.import.id IS 'Id';


--
-- Name: COLUMN import.im_timestamp; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.import.im_timestamp IS 'Import date';


--
-- Name: COLUMN import.fk_id_series; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.import.fk_id_series IS 'Series ID';


--
-- Name: COLUMN import.im_status; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.import.im_status IS 'Status of import : pending, validated';


--
-- Name: import_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.import_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: import_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.import_id_seq OWNED BY gobs.import.id;


--
-- Name: indicator; Type: TABLE; Schema: gobs; Owner: -
--

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


--
-- Name: TABLE indicator; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.indicator IS 'Groups of observation data for decisional purpose. ';


--
-- Name: COLUMN indicator.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id IS 'ID';


--
-- Name: COLUMN indicator.id_label; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_label IS 'Short name';


--
-- Name: COLUMN indicator.id_title; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_title IS 'Title';


--
-- Name: COLUMN indicator.id_description; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_description IS 'Describes the indicator regarding its rôle inside the project.';


--
-- Name: COLUMN indicator.id_date_format; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_date_format IS 'Help to know what is the format for the date. Example : ‘year’';


--
-- Name: COLUMN indicator.id_value_code; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_value_code IS 'List of the codes of the vector dimensions. Ex : [‘pop_h’, ‘pop_f’]';


--
-- Name: COLUMN indicator.id_value_name; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_value_name IS 'List of the names of the vector dimensions. Ex : [‘population homme’, ‘population femme’]';


--
-- Name: COLUMN indicator.id_value_type; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_value_type IS 'Type of the stored values. Ex : ‘integer’ or ‘real’';


--
-- Name: COLUMN indicator.id_value_unit; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.indicator.id_value_unit IS 'Unit ot the store values. Ex : ‘inhabitants’ or ‘°C’';


--
-- Name: indicator_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.indicator_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: indicator_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.indicator_id_seq OWNED BY gobs.indicator.id;


--
-- Name: observation; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.observation (
    id bigint NOT NULL,
    fk_id_series integer NOT NULL,
    fk_id_spatial_object bigint NOT NULL,
    fk_id_import integer NOT NULL,
    ob_value jsonb NOT NULL,
    ob_timestamp timestamp without time zone NOT NULL
);


--
-- Name: TABLE observation; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.observation IS 'Les données brutes au format pivot ( indicateur, date, valeurs et entité spatiale, auteur, etc.)';


--
-- Name: COLUMN observation.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.observation.id IS 'ID';


--
-- Name: COLUMN observation.fk_id_series; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.observation.fk_id_series IS 'Series ID';


--
-- Name: COLUMN observation.fk_id_spatial_object; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.observation.fk_id_spatial_object IS 'ID of the object in the spatial object table';


--
-- Name: COLUMN observation.fk_id_import; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.observation.fk_id_import IS 'Import id';


--
-- Name: COLUMN observation.ob_value; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.observation.ob_value IS 'Vector containing the measured or computed data values. Ex : [1543, 1637]';


--
-- Name: COLUMN observation.ob_timestamp; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.observation.ob_timestamp IS 'Timestamp of the data';


--
-- Name: observation_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.observation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: observation_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.observation_id_seq OWNED BY gobs.observation.id;


--
-- Name: protocol; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.protocol (
    id integer NOT NULL,
    pr_code text NOT NULL,
    pr_name text NOT NULL,
    pr_description text NOT NULL
);


--
-- Name: TABLE protocol; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.protocol IS 'List of protocols';


--
-- Name: COLUMN protocol.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.protocol.id IS 'ID';


--
-- Name: COLUMN protocol.pr_code; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.protocol.pr_code IS 'Code';


--
-- Name: COLUMN protocol.pr_name; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.protocol.pr_name IS 'Name of the indicator';


--
-- Name: COLUMN protocol.pr_description; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.protocol.pr_description IS 'Description, including URLs to references and authors.';


--
-- Name: protocol_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.protocol_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: protocol_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.protocol_id_seq OWNED BY gobs.protocol.id;


--
-- Name: r_graph_edge; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.r_graph_edge (
    ge_parent_node integer NOT NULL,
    ge_child_node integer NOT NULL
);


--
-- Name: TABLE r_graph_edge; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.r_graph_edge IS 'Graph edges: relations between nodes';


--
-- Name: COLUMN r_graph_edge.ge_parent_node; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.r_graph_edge.ge_parent_node IS 'Parent node';


--
-- Name: COLUMN r_graph_edge.ge_child_node; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.r_graph_edge.ge_child_node IS 'Child node';


--
-- Name: r_indicator_node; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.r_indicator_node (
    fk_id_indicator integer NOT NULL,
    fk_id_node integer NOT NULL
);


--
-- Name: TABLE r_indicator_node; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.r_indicator_node IS 'Pivot table between indicators and nodes';


--
-- Name: COLUMN r_indicator_node.fk_id_indicator; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.r_indicator_node.fk_id_indicator IS 'Parent indicator';


--
-- Name: COLUMN r_indicator_node.fk_id_node; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.r_indicator_node.fk_id_node IS 'Parent node';


--
-- Name: series; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.series (
    id integer NOT NULL,
    fk_id_protocol integer NOT NULL,
    fk_id_actor integer NOT NULL,
    fk_id_indicator integer NOT NULL,
    fk_id_spatial_layer integer NOT NULL
);


--
-- Name: TABLE series; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.series IS 'Series of data';


--
-- Name: COLUMN series.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.series.id IS 'Id';


--
-- Name: COLUMN series.fk_id_protocol; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.series.fk_id_protocol IS 'Protocol';


--
-- Name: COLUMN series.fk_id_actor; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.series.fk_id_actor IS 'Actor, source of the observation data.';


--
-- Name: COLUMN series.fk_id_indicator; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.series.fk_id_indicator IS 'Indicator. The series is named after the indicator.';


--
-- Name: COLUMN series.fk_id_spatial_layer; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.series.fk_id_spatial_layer IS 'Spatial layer, mandatory. If needed, use a global spatial layer with only 1 object representing the global area.';


--
-- Name: series_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.series_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: series_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.series_id_seq OWNED BY gobs.series.id;


--
-- Name: spatial_layer; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.spatial_layer (
    id integer NOT NULL,
    sl_code text NOT NULL,
    sl_label text NOT NULL,
    sl_description text NOT NULL,
    sl_creation_date date DEFAULT '2018-06-28'::date NOT NULL,
    fk_id_actor integer NOT NULL,
    sl_geometry_type text NOT NULL
);


--
-- Name: TABLE spatial_layer; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.spatial_layer IS 'List the spatial layers, used to regroup the spatial data. Ex : cities, rivers, stations';


--
-- Name: COLUMN spatial_layer.sl_code; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_layer.sl_code IS 'Unique short code for the spatial layer';


--
-- Name: COLUMN spatial_layer.sl_label; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_layer.sl_label IS 'Label of the spatial layer';


--
-- Name: COLUMN spatial_layer.sl_description; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_layer.sl_description IS 'Description';


--
-- Name: COLUMN spatial_layer.sl_creation_date; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_layer.sl_creation_date IS 'Creation date';


--
-- Name: COLUMN spatial_layer.fk_id_actor; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_layer.fk_id_actor IS 'Source actor.';


--
-- Name: COLUMN spatial_layer.sl_geometry_type; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_layer.sl_geometry_type IS 'Type of geometry (POINT, POLYGON, MULTIPOLYGON, etc.)';


--
-- Name: spatial_layer_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.spatial_layer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: spatial_layer_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.spatial_layer_id_seq OWNED BY gobs.spatial_layer.id;


--
-- Name: spatial_object; Type: TABLE; Schema: gobs; Owner: -
--

CREATE TABLE gobs.spatial_object (
    id bigint NOT NULL,
    so_unique_id text NOT NULL,
    so_unique_label text NOT NULL,
    geom public.geometry(Geometry,4326) NOT NULL,
    fk_id_spatial_layer integer NOT NULL
);


--
-- Name: TABLE spatial_object; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON TABLE gobs.spatial_object IS 'Contains all the spatial objects, caracterized by a geometry type and an entity';


--
-- Name: COLUMN spatial_object.id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_object.id IS 'ID';


--
-- Name: COLUMN spatial_object.so_unique_id; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_object.so_unique_id IS 'Unique code of each object in the spatial layer ( INSEE, tag, etc.)';


--
-- Name: COLUMN spatial_object.so_unique_label; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_object.so_unique_label IS 'Label of each spatial object. Ex : name of the city.';


--
-- Name: COLUMN spatial_object.geom; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_object.geom IS 'Geometry of the spatial object. Alway in EPSG:4326';


--
-- Name: COLUMN spatial_object.fk_id_spatial_layer; Type: COMMENT; Schema: gobs; Owner: -
--

COMMENT ON COLUMN gobs.spatial_object.fk_id_spatial_layer IS 'Spatial layer';


--
-- Name: spatial_object_id_seq; Type: SEQUENCE; Schema: gobs; Owner: -
--

CREATE SEQUENCE gobs.spatial_object_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: spatial_object_id_seq; Type: SEQUENCE OWNED BY; Schema: gobs; Owner: -
--

ALTER SEQUENCE gobs.spatial_object_id_seq OWNED BY gobs.spatial_object.id;


--
-- Name: actor id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.actor ALTER COLUMN id SET DEFAULT nextval('gobs.actor_id_seq'::regclass);


--
-- Name: actor_category id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.actor_category ALTER COLUMN id SET DEFAULT nextval('gobs.actor_category_id_seq'::regclass);


--
-- Name: glossary id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.glossary ALTER COLUMN id SET DEFAULT nextval('gobs.glossary_id_seq'::regclass);


--
-- Name: graph_node id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.graph_node ALTER COLUMN id SET DEFAULT nextval('gobs.graph_node_id_seq'::regclass);


--
-- Name: import id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.import ALTER COLUMN id SET DEFAULT nextval('gobs.import_id_seq'::regclass);


--
-- Name: indicator id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.indicator ALTER COLUMN id SET DEFAULT nextval('gobs.indicator_id_seq'::regclass);


--
-- Name: observation id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.observation ALTER COLUMN id SET DEFAULT nextval('gobs.observation_id_seq'::regclass);


--
-- Name: protocol id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.protocol ALTER COLUMN id SET DEFAULT nextval('gobs.protocol_id_seq'::regclass);


--
-- Name: series id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.series ALTER COLUMN id SET DEFAULT nextval('gobs.series_id_seq'::regclass);


--
-- Name: spatial_layer id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.spatial_layer ALTER COLUMN id SET DEFAULT nextval('gobs.spatial_layer_id_seq'::regclass);


--
-- Name: spatial_object id; Type: DEFAULT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.spatial_object ALTER COLUMN id SET DEFAULT nextval('gobs.spatial_object_id_seq'::regclass);


--
-- Name: actor_category actor_category_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.actor_category
    ADD CONSTRAINT actor_category_pkey PRIMARY KEY (id);


--
-- Name: actor actor_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_pkey PRIMARY KEY (id);


--
-- Name: glossary glossary_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.glossary
    ADD CONSTRAINT glossary_pkey PRIMARY KEY (id);


--
-- Name: graph_node graph_node_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.graph_node
    ADD CONSTRAINT graph_node_pkey PRIMARY KEY (id);


--
-- Name: import import_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.import
    ADD CONSTRAINT import_pkey PRIMARY KEY (id);


--
-- Name: indicator indicator_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.indicator
    ADD CONSTRAINT indicator_pkey PRIMARY KEY (id);


--
-- Name: observation observation_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_pkey PRIMARY KEY (id);


--
-- Name: protocol protocol_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.protocol
    ADD CONSTRAINT protocol_pkey PRIMARY KEY (id);


--
-- Name: r_graph_edge r_graph_edge_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.r_graph_edge
    ADD CONSTRAINT r_graph_edge_pkey PRIMARY KEY (ge_parent_node, ge_child_node);


--
-- Name: r_indicator_node r_indicator_node_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_pkey PRIMARY KEY (fk_id_indicator, fk_id_node);


--
-- Name: series series_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_pkey PRIMARY KEY (id);


--
-- Name: spatial_layer spatial_layer_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.spatial_layer
    ADD CONSTRAINT spatial_layer_pkey PRIMARY KEY (id);


--
-- Name: spatial_object spatial_object_pkey; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_pkey PRIMARY KEY (id);


--
-- Name: spatial_object spatial_object_so_unique_id_fk_id_spatial_layer_key; Type: CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_so_unique_id_fk_id_spatial_layer_key UNIQUE (so_unique_id, fk_id_spatial_layer);


--
-- Name: actor_a_name_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX actor_a_name_idx ON gobs.actor USING btree (a_name);


--
-- Name: glossary_gl_field_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX glossary_gl_field_idx ON gobs.glossary USING btree (gl_field);


--
-- Name: graph_node_gn_name_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX graph_node_gn_name_idx ON gobs.graph_node USING btree (gn_name);


--
-- Name: import_fk_id_series_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX import_fk_id_series_idx ON gobs.import USING btree (fk_id_series);


--
-- Name: indicator_id_label_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX indicator_id_label_idx ON gobs.indicator USING btree (id_label);


--
-- Name: observation_fk_id_import_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX observation_fk_id_import_idx ON gobs.observation USING btree (fk_id_import);


--
-- Name: observation_fk_id_series_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX observation_fk_id_series_idx ON gobs.observation USING btree (fk_id_series);


--
-- Name: observation_fk_id_spatial_object_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX observation_fk_id_spatial_object_idx ON gobs.observation USING btree (fk_id_spatial_object);


--
-- Name: observation_ob_timestamp_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX observation_ob_timestamp_idx ON gobs.observation USING btree (ob_timestamp);


--
-- Name: protocol_pr_code_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX protocol_pr_code_idx ON gobs.protocol USING btree (pr_code);


--
-- Name: series_fk_id_actor_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX series_fk_id_actor_idx ON gobs.series USING btree (fk_id_actor);


--
-- Name: series_fk_id_indicator_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX series_fk_id_indicator_idx ON gobs.series USING btree (fk_id_indicator);


--
-- Name: series_fk_id_protocol_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX series_fk_id_protocol_idx ON gobs.series USING btree (fk_id_protocol);


--
-- Name: series_fk_id_spatial_layer_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX series_fk_id_spatial_layer_idx ON gobs.series USING btree (fk_id_spatial_layer);


--
-- Name: spatial_layer_sl_code_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX spatial_layer_sl_code_idx ON gobs.spatial_layer USING btree (sl_code);


--
-- Name: spatial_object_fk_id_spatial_layer_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX spatial_object_fk_id_spatial_layer_idx ON gobs.spatial_object USING btree (fk_id_spatial_layer);


--
-- Name: spatial_object_geom_idx; Type: INDEX; Schema: gobs; Owner: -
--

CREATE INDEX spatial_object_geom_idx ON gobs.spatial_object USING btree (geom);


--
-- Name: actor actor_id_category_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.actor
    ADD CONSTRAINT actor_id_category_fkey FOREIGN KEY (id_category) REFERENCES gobs.actor_category(id) ON DELETE RESTRICT;


--
-- Name: import import_fk_id_series_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.import
    ADD CONSTRAINT import_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;


--
-- Name: observation observation_fk_id_import_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_import_fkey FOREIGN KEY (fk_id_import) REFERENCES gobs.import(id) ON DELETE RESTRICT;


--
-- Name: observation observation_fk_id_series_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_series_fkey FOREIGN KEY (fk_id_series) REFERENCES gobs.series(id) ON DELETE RESTRICT;


--
-- Name: observation observation_fk_id_spatial_object_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.observation
    ADD CONSTRAINT observation_fk_id_spatial_object_fkey FOREIGN KEY (fk_id_spatial_object) REFERENCES gobs.spatial_object(id) ON DELETE RESTRICT;


--
-- Name: r_indicator_node r_indicator_node_fk_id_indicator_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE CASCADE;


--
-- Name: r_indicator_node r_indicator_node_fk_id_node_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.r_indicator_node
    ADD CONSTRAINT r_indicator_node_fk_id_node_fkey FOREIGN KEY (fk_id_node) REFERENCES gobs.graph_node(id) ON DELETE CASCADE;


--
-- Name: series series_fk_id_actor_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;


--
-- Name: series series_fk_id_indicator_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id) ON DELETE RESTRICT;


--
-- Name: series series_fk_id_protocol_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_protocol_fkey FOREIGN KEY (fk_id_protocol) REFERENCES gobs.protocol(id) ON DELETE RESTRICT;


--
-- Name: series series_fk_id_spatial_layer_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.series
    ADD CONSTRAINT series_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;


--
-- Name: spatial_layer spatial_layer_fk_id_actor_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.spatial_layer
    ADD CONSTRAINT spatial_layer_fk_id_actor_fkey FOREIGN KEY (fk_id_actor) REFERENCES gobs.actor(id) ON DELETE RESTRICT;


--
-- Name: spatial_object spatial_object_fk_id_spatial_layer_fkey; Type: FK CONSTRAINT; Schema: gobs; Owner: -
--

ALTER TABLE ONLY gobs.spatial_object
    ADD CONSTRAINT spatial_object_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer) REFERENCES gobs.spatial_layer(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

