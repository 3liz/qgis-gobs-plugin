BEGIN;



-- Table actor_category 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "actor_category" () ;

COMMENT ON TABLE "actor_category" IS 'Actors categories' ;

ALTER TABLE "actor_category" ADD COLUMN "id" serial NOT NULL ;
COMMENT ON COLUMN "actor_category"."id" IS 'ID' ; 

ALTER TABLE "actor_category" ADD COLUMN "ac_name" text NOT NULL ;
COMMENT ON COLUMN "actor_category"."ac_name" IS 'Name of the actor category' ; 

ALTER TABLE "actor_category" ADD COLUMN "ac_description" text NOT NULL ;
COMMENT ON COLUMN "actor_category"."ac_description" IS 'Description of the actor category' ; 

ALTER TABLE "actor_category" ADD PRIMARY KEY ("id");


-- Table actor 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "actor" () ;

COMMENT ON TABLE "actor" IS 'Actors' ;

ALTER TABLE "actor" ADD COLUMN "id" serial NOT NULL ;
COMMENT ON COLUMN "actor"."id" IS 'ID' ; 

ALTER TABLE "actor" ADD COLUMN "a_name" text NOT NULL ;
COMMENT ON COLUMN "actor"."a_name" IS 'Name of the actor (can be a person or an entity)' ; 
CREATE INDEX ON "actor" ("a_name") ;

ALTER TABLE "actor" ADD COLUMN "a_description" text NOT NULL ;
COMMENT ON COLUMN "actor"."a_description" IS 'Description of the actor' ; 

ALTER TABLE "actor" ADD COLUMN "a_email" text NOT NULL ;
COMMENT ON COLUMN "actor"."a_email" IS 'Email of the actor' ; 

ALTER TABLE "actor" ADD COLUMN "id_category" integer NOT NULL ;
COMMENT ON COLUMN "actor"."id_category" IS 'Category of actor' ; 

ALTER TABLE "actor" ADD PRIMARY KEY ("id");


-- Table protocol 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "protocol" () ;

COMMENT ON TABLE "protocol" IS 'List of protocols' ;

ALTER TABLE "protocol" ADD COLUMN "id" serial NOT NULL ;
COMMENT ON COLUMN "protocol"."id" IS 'ID' ; 

ALTER TABLE "protocol" ADD COLUMN "pr_code" text NOT NULL ;
COMMENT ON COLUMN "protocol"."pr_code" IS 'Code' ; 
CREATE INDEX ON "protocol" ("pr_code") ;

ALTER TABLE "protocol" ADD COLUMN "pr_name" text NOT NULL ;
COMMENT ON COLUMN "protocol"."pr_name" IS 'Name of the indicator' ; 

ALTER TABLE "protocol" ADD COLUMN "pr_description" text NOT NULL ;
COMMENT ON COLUMN "protocol"."pr_description" IS 'Description, including URLs to references and authors.' ; 

ALTER TABLE "protocol" ADD PRIMARY KEY ("id");


-- Table series 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "series" () ;

COMMENT ON TABLE "series" IS 'Series of data' ;

ALTER TABLE "series" ADD COLUMN "id" serial  ;
COMMENT ON COLUMN "series"."id" IS 'Id' ; 

ALTER TABLE "series" ADD COLUMN "fk_id_protocol" integer NOT NULL ;
COMMENT ON COLUMN "series"."fk_id_protocol" IS 'Protocol' ; 
CREATE INDEX ON "series" ("fk_id_protocol") ;

ALTER TABLE "series" ADD COLUMN "fk_id_actor" integer NOT NULL ;
COMMENT ON COLUMN "series"."fk_id_actor" IS 'Actor, source of the observation data.' ; 
CREATE INDEX ON "series" ("fk_id_actor") ;

ALTER TABLE "series" ADD COLUMN "fk_id_indicator" integer NOT NULL ;
COMMENT ON COLUMN "series"."fk_id_indicator" IS 'Indicator. The series is named after the indicator.' ; 
CREATE INDEX ON "series" ("fk_id_indicator") ;

ALTER TABLE "series" ADD COLUMN "fk_id_spatial_layer" integer NOT NULL ;
COMMENT ON COLUMN "series"."fk_id_spatial_layer" IS 'Spatial layer, mandatory. If needed, use a global spatial layer with only 1 object representing the global area.' ; 
CREATE INDEX ON "series" ("fk_id_spatial_layer") ;

ALTER TABLE "series" ADD PRIMARY KEY ("id");


-- Table import 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "import" () ;

COMMENT ON TABLE "import" IS 'Journal des imports' ;

ALTER TABLE "import" ADD COLUMN "id" serial NOT NULL ;
COMMENT ON COLUMN "import"."id" IS 'Id' ; 

ALTER TABLE "import" ADD COLUMN "im_timestamp" timestamp NOT NULL ;
ALTER TABLE "import" ALTER COLUMN "im_timestamp" SET DEFAULT 'now()';  
COMMENT ON COLUMN "import"."im_timestamp" IS 'Import date' ; 

ALTER TABLE "import" ADD COLUMN "fk_id_series" integer NOT NULL ;
COMMENT ON COLUMN "import"."fk_id_series" IS 'Series ID' ; 
CREATE INDEX ON "import" ("fk_id_series") ;

ALTER TABLE "import" ADD COLUMN "im_status" text  ;
ALTER TABLE "import" ALTER COLUMN "im_status" SET DEFAULT 'p';  
COMMENT ON COLUMN "import"."im_status" IS 'Status of import : pending, validated' ; 

ALTER TABLE "import" ADD PRIMARY KEY ("id");


-- Table indicator 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "indicator" () ;

COMMENT ON TABLE "indicator" IS 'Groups of observation data for decisional purpose. ' ;

ALTER TABLE "indicator" ADD COLUMN "id" serial NOT NULL ;
COMMENT ON COLUMN "indicator"."id" IS 'ID' ; 

ALTER TABLE "indicator" ADD COLUMN "id_label" text NOT NULL ;
COMMENT ON COLUMN "indicator"."id_label" IS 'Short name' ; 
CREATE INDEX ON "indicator" ("id_label") ;

ALTER TABLE "indicator" ADD COLUMN "id_title" text NOT NULL ;
COMMENT ON COLUMN "indicator"."id_title" IS 'Title' ; 

ALTER TABLE "indicator" ADD COLUMN "id_description" text NOT NULL ;
COMMENT ON COLUMN "indicator"."id_description" IS 'Describes the indicator regarding its rôle inside the project.' ; 

ALTER TABLE "indicator" ADD COLUMN "id_date_format" text NOT NULL ;
ALTER TABLE "indicator" ALTER COLUMN "id_date_format" SET DEFAULT 'day';  
COMMENT ON COLUMN "indicator"."id_date_format" IS 'Help to know what is the format for the date. Example : ‘year’' ; 

ALTER TABLE "indicator" ADD COLUMN "id_value_code" jsonb NOT NULL ;
COMMENT ON COLUMN "indicator"."id_value_code" IS 'List of the codes of the vector dimensions. Ex : [‘pop_h’, ‘pop_f’]' ; 

ALTER TABLE "indicator" ADD COLUMN "id_value_name" jsonb NOT NULL ;
COMMENT ON COLUMN "indicator"."id_value_name" IS 'List of the names of the vector dimensions. Ex : [‘population homme’, ‘population femme’]' ; 

ALTER TABLE "indicator" ADD COLUMN "id_value_type" text NOT NULL ;
ALTER TABLE "indicator" ALTER COLUMN "id_value_type" SET DEFAULT 'integer';  
COMMENT ON COLUMN "indicator"."id_value_type" IS 'Type of the stored values. Ex : ‘integer’ or ‘real’' ; 

ALTER TABLE "indicator" ADD COLUMN "id_value_unit" text NOT NULL ;
COMMENT ON COLUMN "indicator"."id_value_unit" IS 'Unit ot the store values. Ex : ‘inhabitants’ or ‘°C’' ; 

ALTER TABLE "indicator" ADD PRIMARY KEY ("id");


-- Table spatial_layer 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "spatial_layer" () ;

COMMENT ON TABLE "spatial_layer" IS 'List the spatial layers, used to regroup the spatial data. Ex : cities, rivers, stations' ;

ALTER TABLE "spatial_layer" ADD COLUMN "id" serial NOT NULL ;

ALTER TABLE "spatial_layer" ADD COLUMN "sl_code" text NOT NULL ;
COMMENT ON COLUMN "spatial_layer"."sl_code" IS 'Unique short code for the spatial layer' ; 
CREATE INDEX ON "spatial_layer" ("sl_code") ;

ALTER TABLE "spatial_layer" ADD COLUMN "sl_label" text NOT NULL ;
COMMENT ON COLUMN "spatial_layer"."sl_label" IS 'Label of the spatial layer' ; 

ALTER TABLE "spatial_layer" ADD COLUMN "sl_description" text NOT NULL ;
COMMENT ON COLUMN "spatial_layer"."sl_description" IS 'Description' ; 

ALTER TABLE "spatial_layer" ADD COLUMN "sl_creation_date" date NOT NULL ;
ALTER TABLE "spatial_layer" ALTER COLUMN "sl_creation_date" SET DEFAULT 'now()';  
COMMENT ON COLUMN "spatial_layer"."sl_creation_date" IS 'Creation date' ; 

ALTER TABLE "spatial_layer" ADD COLUMN "fk_id_actor" integer NOT NULL ;
COMMENT ON COLUMN "spatial_layer"."fk_id_actor" IS 'Source actor.' ; 

ALTER TABLE "spatial_layer" ADD COLUMN "sl_geometry_type" text NOT NULL ;
COMMENT ON COLUMN "spatial_layer"."sl_geometry_type" IS 'Type of geometry (POINT, POLYGON, MULTIPOLYGON, etc.)' ; 

ALTER TABLE "spatial_layer" ADD PRIMARY KEY ("id");


-- Table spatial_object 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "spatial_object" () ;

COMMENT ON TABLE "spatial_object" IS 'Contains all the spatial objects, caracterized by a geometry type and an entity' ;

ALTER TABLE "spatial_object" ADD COLUMN "id" bigserial NOT NULL ;
COMMENT ON COLUMN "spatial_object"."id" IS 'ID' ; 

ALTER TABLE "spatial_object" ADD COLUMN "so_unique_id" text NOT NULL ;
COMMENT ON COLUMN "spatial_object"."so_unique_id" IS 'Unique code of each object in the spatial layer ( INSEE, tag, etc.)' ; 

ALTER TABLE "spatial_object" ADD COLUMN "so_unique_label" text NOT NULL ;
COMMENT ON COLUMN "spatial_object"."so_unique_label" IS 'Label of each spatial object. Ex : name of the city.' ; 

ALTER TABLE "spatial_object" ADD COLUMN "geom" geometry(GEOMETRY,4326) NOT NULL ;
COMMENT ON COLUMN "spatial_object"."geom" IS 'Geometry of the spatial object. Alway in EPSG:4326' ; 
CREATE INDEX ON "spatial_object" ("geom") ;

ALTER TABLE "spatial_object" ADD COLUMN "fk_id_spatial_layer" integer NOT NULL ;
COMMENT ON COLUMN "spatial_object"."fk_id_spatial_layer" IS 'Spatial layer' ; 
CREATE INDEX ON "spatial_object" ("fk_id_spatial_layer") ;

ALTER TABLE "spatial_object" ADD PRIMARY KEY ("id");


-- Table observation 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "observation" () ;

COMMENT ON TABLE "observation" IS 'Les données brutes au format pivot ( indicateur, date, valeurs et entité spatiale, auteur, etc.)' ;

ALTER TABLE "observation" ADD COLUMN "id" bigserial NOT NULL ;
COMMENT ON COLUMN "observation"."id" IS 'ID' ; 

ALTER TABLE "observation" ADD COLUMN "fk_id_series" integer NOT NULL ;
COMMENT ON COLUMN "observation"."fk_id_series" IS 'Series ID' ; 
CREATE INDEX ON "observation" ("fk_id_series") ;

ALTER TABLE "observation" ADD COLUMN "fk_id_spatial_object" bigint NOT NULL ;
COMMENT ON COLUMN "observation"."fk_id_spatial_object" IS 'ID of the object in the spatial object table' ; 
CREATE INDEX ON "observation" ("fk_id_spatial_object") ;

ALTER TABLE "observation" ADD COLUMN "fk_id_import" integer NOT NULL ;
COMMENT ON COLUMN "observation"."fk_id_import" IS 'Import id' ; 
CREATE INDEX ON "observation" ("fk_id_import") ;

ALTER TABLE "observation" ADD COLUMN "ob_value" jsonb NOT NULL ;
COMMENT ON COLUMN "observation"."ob_value" IS 'Vector containing the measured or computed data values. Ex : [1543, 1637]' ; 

ALTER TABLE "observation" ADD COLUMN "ob_timestamp" timestamp NOT NULL ;
COMMENT ON COLUMN "observation"."ob_timestamp" IS 'Timestamp of the data' ; 
CREATE INDEX ON "observation" ("ob_timestamp") ;

ALTER TABLE "observation" ADD PRIMARY KEY ("id");


-- Table glossary 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "glossary" () ;

COMMENT ON TABLE "glossary" IS 'List of labels and words used as labels for stored data' ;

ALTER TABLE "glossary" ADD COLUMN "id" serial NOT NULL ;
COMMENT ON COLUMN "glossary"."id" IS 'ID' ; 

ALTER TABLE "glossary" ADD COLUMN "gl_field" text NOT NULL ;
COMMENT ON COLUMN "glossary"."gl_field" IS 'Field' ; 
CREATE INDEX ON "glossary" ("gl_field") ;

ALTER TABLE "glossary" ADD COLUMN "gl_code" text NOT NULL ;
COMMENT ON COLUMN "glossary"."gl_code" IS 'Code' ; 

ALTER TABLE "glossary" ADD COLUMN "gl_value" text NOT NULL ;
COMMENT ON COLUMN "glossary"."gl_value" IS 'Value' ; 

ALTER TABLE "glossary" ADD COLUMN "gl_label" text NOT NULL ;
COMMENT ON COLUMN "glossary"."gl_label" IS 'Label' ; 

ALTER TABLE "glossary" ADD COLUMN "gl_order" smallint  ;
COMMENT ON COLUMN "glossary"."gl_order" IS 'Order' ; 

ALTER TABLE "glossary" ADD PRIMARY KEY ("id");


-- Table graph_node 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "graph_node" () ;

COMMENT ON TABLE "graph_node" IS 'Graph nodes, to store key words used to find an indicator.' ;

ALTER TABLE "graph_node" ADD COLUMN "id" serial NOT NULL ;
COMMENT ON COLUMN "graph_node"."id" IS 'ID' ; 

ALTER TABLE "graph_node" ADD COLUMN "gn_name" text NOT NULL ;
COMMENT ON COLUMN "graph_node"."gn_name" IS 'Name of the node' ; 
CREATE INDEX ON "graph_node" ("gn_name") ;

ALTER TABLE "graph_node" ADD COLUMN "gn_description" text NOT NULL ;
COMMENT ON COLUMN "graph_node"."gn_description" IS 'Description of the node' ; 

ALTER TABLE "graph_node" ADD PRIMARY KEY ("id");


-- Table r_graph_edge 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "r_graph_edge" () ;

COMMENT ON TABLE "r_graph_edge" IS 'Graph edges: relations between nodes' ;

ALTER TABLE "r_graph_edge" ADD COLUMN "ge_parent_node" integer NOT NULL ;
COMMENT ON COLUMN "r_graph_edge"."ge_parent_node" IS 'Parent node' ; 

ALTER TABLE "r_graph_edge" ADD COLUMN "ge_child_node" integer NOT NULL ;
COMMENT ON COLUMN "r_graph_edge"."ge_child_node" IS 'Child node' ; 

ALTER TABLE "r_graph_edge" ADD PRIMARY KEY ("ge_parent_node", "ge_child_node");


-- Table r_indicator_node 
CREATE SCHEMA IF NOT EXISTS "gobs" ;
SET search_path TO gobs,public ;
CREATE TABLE IF NOT EXISTS "r_indicator_node" () ;

COMMENT ON TABLE "r_indicator_node" IS 'Pivot table between indicators and nodes' ;

ALTER TABLE "r_indicator_node" ADD COLUMN "fk_id_indicator" integer NOT NULL ;
COMMENT ON COLUMN "r_indicator_node"."fk_id_indicator" IS 'Parent indicator' ; 

ALTER TABLE "r_indicator_node" ADD COLUMN "fk_id_node" integer NOT NULL ;
COMMENT ON COLUMN "r_indicator_node"."fk_id_node" IS 'Parent node' ; 

ALTER TABLE "r_indicator_node" ADD PRIMARY KEY ("fk_id_indicator", "fk_id_node");

ALTER TABLE "actor" ADD CONSTRAINT actor_id_category_fkey FOREIGN KEY (id_category)  REFERENCES "actor_category" (id) ON DELETE restrict ; 

ALTER TABLE "series" ADD CONSTRAINT series_fk_id_protocol_fkey FOREIGN KEY (fk_id_protocol)  REFERENCES "protocol" (id) ON DELETE restrict ; 

ALTER TABLE "series" ADD CONSTRAINT series_fk_id_actor_fkey FOREIGN KEY (fk_id_actor)  REFERENCES "actor" (id) ON DELETE restrict ; 

ALTER TABLE "series" ADD CONSTRAINT series_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator)  REFERENCES "indicator" (id) ON DELETE restrict ; 

ALTER TABLE "series" ADD CONSTRAINT series_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer)  REFERENCES "spatial_layer" (id) ON DELETE restrict ; 

ALTER TABLE "import" ADD CONSTRAINT import_fk_id_series_fkey FOREIGN KEY (fk_id_series)  REFERENCES "series" (id) ON DELETE restrict ; 

ALTER TABLE "spatial_layer" ADD CONSTRAINT spatial_layer_fk_id_actor_fkey FOREIGN KEY (fk_id_actor)  REFERENCES "actor" (id) ON DELETE restrict ; 

ALTER TABLE "spatial_object" ADD CONSTRAINT spatial_object_fk_id_spatial_layer_fkey FOREIGN KEY (fk_id_spatial_layer)  REFERENCES "spatial_layer" (id) ON DELETE restrict ; 

ALTER TABLE "observation" ADD CONSTRAINT observation_fk_id_series_fkey FOREIGN KEY (fk_id_series)  REFERENCES "series" (id) ON DELETE restrict ; 

ALTER TABLE "observation" ADD CONSTRAINT observation_fk_id_spatial_object_fkey FOREIGN KEY (fk_id_spatial_object)  REFERENCES "spatial_object" (id) ON DELETE restrict ; 

ALTER TABLE "observation" ADD CONSTRAINT observation_fk_id_import_fkey FOREIGN KEY (fk_id_import)  REFERENCES "import" (id) ON DELETE restrict ; 

ALTER TABLE "r_indicator_node" ADD CONSTRAINT r_indicator_node_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator)  REFERENCES "indicator" (id) ON DELETE cascade ; 

ALTER TABLE "r_indicator_node" ADD CONSTRAINT r_indicator_node_fk_id_node_fkey FOREIGN KEY (fk_id_node)  REFERENCES "graph_node" (id) ON DELETE cascade ; 

COMMIT;