BEGIN;

DROP TABLE IF EXISTS gobs.project CASCADE;
CREATE TABLE gobs.project (
    id serial NOT NULL primary key,
    pt_code text NOT NULL UNIQUE,
    pt_lizmap_project_key text,
    pt_label text NOT NULL UNIQUE,
    pt_description text,
    pt_indicator_codes text[],
    pt_groups text,
    pt_xmin real,
    pt_ymin real,
    pt_xmax real,
    pt_ymax real
);

COMMENT ON TABLE gobs.project
IS 'List of projects, which represents a group of indicators'
;

COMMENT ON COLUMN gobs.project.id IS 'Unique identifier';
COMMENT ON COLUMN gobs.project.pt_code IS 'Project code. Ex: weather_data';
COMMENT ON COLUMN gobs.project.pt_lizmap_project_key IS 'Lizmap project unique identifier (optional): repository_code~project_file_name. Ex: environment~weather';
COMMENT ON COLUMN gobs.project.pt_label IS 'Human readable label of the project. Ex: Weather data publication';
COMMENT ON COLUMN gobs.project.pt_description IS 'Description of the project.';
COMMENT ON COLUMN gobs.project.pt_indicator_codes IS 'List of indicator codes available for this project';
COMMENT ON COLUMN gobs.project.pt_groups IS 'List of groups of users which have access to the project and its indicators, separated by coma.';
COMMENT ON COLUMN gobs.project.pt_xmin IS 'Minimum longitude (X min) in EPSG:4326';
COMMENT ON COLUMN gobs.project.pt_ymin IS 'Minimum latitude (Y min) in EPSG:4326';
COMMENT ON COLUMN gobs.project.pt_xmax IS 'Maximum longitude (X max) in EPSG:4326';
COMMENT ON COLUMN gobs.project.pt_ymax IS 'Maximum latitude (Y max) in EPSG:4326';


DROP TABLE IF EXISTS gobs.project_view;
CREATE TABLE gobs.project_view (
    id serial NOT NULL PRIMARY KEY,
    pv_label text NOT NULL,
    fk_id_project integer NOT NULL REFERENCES gobs.project (id) ON DELETE CASCADE,
    pv_groups text,
    fk_id_spatial_layer integer REFERENCES gobs.spatial_layer (id) ON DELETE SET NULL,
    fk_so_unique_id text
);

COMMENT ON TABLE gobs.project_view
IS 'Allow to filter the access on projects and relative data (indicators, observations, etc.) with a spatial object for a given list of user groups'
;

ALTER TABLE gobs.project_view ADD UNIQUE (fk_id_project, fk_id_spatial_layer, fk_so_unique_id);

COMMENT ON COLUMN gobs.project_view.id IS 'Unique identifier';
COMMENT ON COLUMN gobs.project_view.pv_label IS 'Label of the project view';
COMMENT ON COLUMN gobs.project_view.fk_id_project IS 'Project id (foreign key)';
COMMENT ON COLUMN gobs.project_view.pv_groups IS 'List of user groups allowed to see observation data inside this project view spatial layer object. Use a coma separated value. Ex: "group_a, group_b"';
COMMENT ON COLUMN gobs.project_view.fk_id_spatial_layer IS 'Spatial layer id (foreign key)';
COMMENT ON COLUMN gobs.project_view.fk_so_unique_id IS 'Spatial object unique id (foreign key). Ex: AB1234. This references the object unique code, not the object integer id field';


-- Table application
DROP TABLE IF EXISTS gobs.application;
CREATE TABLE gobs.application (
    id serial NOT NULL PRIMARY KEY,
    ap_code text NOT NULL,
    ap_label text NOT NULL,
    ap_description text NOT NULL,
    ap_default_values jsonb NOT NULL
)
;

COMMENT ON TABLE gobs.application
IS 'List the external applications interacting with G-Obs database with the web API.
This will help storing application specific data such as the default values when creating automatically series, protocols, users, etc.'
;

COMMENT ON COLUMN gobs.application.id IS 'Unique identifier';
COMMENT ON COLUMN gobs.application.ap_code IS 'Code of the application. Ex: kobo_toolbox';
COMMENT ON COLUMN gobs.application.ap_label IS 'Label of the application. Ex: Kobo Toolbox';
COMMENT ON COLUMN gobs.application.ap_description IS 'Description of the application.';
COMMENT ON COLUMN gobs.application.ap_default_values IS 'Default values for the different API need. JSONB to allow to easily add more data when necessary';
COMMIT;
