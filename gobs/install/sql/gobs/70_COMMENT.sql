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

-- FUNCTION find_observation_with_wrong_spatial_object(_id_series integer)
COMMENT ON FUNCTION gobs.find_observation_with_wrong_spatial_object(_id_series integer) IS 'Find the observations with having incompatible start and end timestamp with related spatial objects validity dates';


-- FUNCTION update_observations_with_wrong_spatial_objects(_id_series integer)
COMMENT ON FUNCTION gobs.update_observations_with_wrong_spatial_objects(_id_series integer) IS 'Update observations with wrong spatial objects: it search the observation for which the start and end timestamp does not match anymore the related spatial objects validity dates. It gets the correct one if possible and perform an UPDATE for these observations. It returns a line with 2 integer columns: modified_obs_count (number of modified observations) and remaining_obs_count (number of observations still with wrong observations';


-- actor
COMMENT ON TABLE gobs.actor IS 'Actors';


-- actor.id
COMMENT ON COLUMN gobs.actor.id IS 'ID';


-- actor.a_label
COMMENT ON COLUMN gobs.actor.a_label IS 'Name of the actor (can be a person or an entity)';


-- actor.a_description
COMMENT ON COLUMN gobs.actor.a_description IS 'Description of the actor';


-- actor.a_email
COMMENT ON COLUMN gobs.actor.a_email IS 'Email of the actor';


-- actor.id_category
COMMENT ON COLUMN gobs.actor.id_category IS 'Category of actor';


-- actor.a_login
COMMENT ON COLUMN gobs.actor.a_login IS 'Login of the actor. It is the unique identifier of the actor.';


-- actor_category
COMMENT ON TABLE gobs.actor_category IS 'Actors categories';


-- actor_category.id
COMMENT ON COLUMN gobs.actor_category.id IS 'ID';


-- actor_category.ac_label
COMMENT ON COLUMN gobs.actor_category.ac_label IS 'Name of the actor category';


-- actor_category.ac_description
COMMENT ON COLUMN gobs.actor_category.ac_description IS 'Description of the actor category';


-- application
COMMENT ON TABLE gobs.application IS 'List the external applications interacting with G-Obs database with the web API.
This will help storing application specific data such as the default values when creating automatically series, protocols, users, etc.';


-- application.id
COMMENT ON COLUMN gobs.application.id IS 'Unique identifier';


-- application.ap_code
COMMENT ON COLUMN gobs.application.ap_code IS 'Code of the application. Ex: kobo_toolbox';


-- application.ap_label
COMMENT ON COLUMN gobs.application.ap_label IS 'Label of the application. Ex: Kobo Toolbox';


-- application.ap_description
COMMENT ON COLUMN gobs.application.ap_description IS 'Description of the application.';


-- application.ap_default_values
COMMENT ON COLUMN gobs.application.ap_default_values IS 'Default values for the different API need. JSONB to allow to easily add more data when necessary';


-- deleted_data_log
COMMENT ON TABLE gobs.deleted_data_log IS 'Log of deleted objects from observation table. Use for synchronization purpose';


-- deleted_data_log.de_table
COMMENT ON COLUMN gobs.deleted_data_log.de_table IS 'Source table of the deleted object: observation';


-- deleted_data_log.de_uid
COMMENT ON COLUMN gobs.deleted_data_log.de_uid IS 'Unique text identifier of the object. Observation: ob_uid';


-- deleted_data_log.de_timestamp
COMMENT ON COLUMN gobs.deleted_data_log.de_timestamp IS 'Timestamp of the deletion';


-- document
COMMENT ON TABLE gobs.document IS 'List of documents for describing indicators.';


-- document.id
COMMENT ON COLUMN gobs.document.id IS 'ID';


-- document.do_uid
COMMENT ON COLUMN gobs.document.do_uid IS 'Document uid: autogenerated unique identifier';


-- document.do_label
COMMENT ON COLUMN gobs.document.do_label IS 'Label of the document, used for display. Must be unique';


-- document.do_description
COMMENT ON COLUMN gobs.document.do_description IS 'Description of the document';


-- document.do_type
COMMENT ON COLUMN gobs.document.do_type IS 'Type of the document';


-- document.do_path
COMMENT ON COLUMN gobs.document.do_path IS 'Relative path of the document to the project storage. Ex: media/indicator/documents/indicator_weather_status_description.pdf';


-- document.fk_id_indicator
COMMENT ON COLUMN gobs.document.fk_id_indicator IS 'Indicator id';


-- document.created_at
COMMENT ON COLUMN gobs.document.created_at IS 'Creation timestamp';


-- document.updated_at
COMMENT ON COLUMN gobs.document.updated_at IS 'Last updated timestamp';


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


-- graph_node
COMMENT ON TABLE gobs.graph_node IS 'Graph nodes, to store key words used to find an indicator.';


-- graph_node.id
COMMENT ON COLUMN gobs.graph_node.id IS 'ID';


-- graph_node.gn_label
COMMENT ON COLUMN gobs.graph_node.gn_label IS 'Name of the node';


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


-- indicator
COMMENT ON TABLE gobs.indicator IS 'Groups of observation data for decisional purpose. ';


-- indicator.id
COMMENT ON COLUMN gobs.indicator.id IS 'ID';


-- indicator.id_code
COMMENT ON COLUMN gobs.indicator.id_code IS 'Short name';


-- indicator.id_label
COMMENT ON COLUMN gobs.indicator.id_label IS 'Title';


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


-- indicator.id_category
COMMENT ON COLUMN gobs.indicator.id_category IS 'Category of the indicator. Used to group several indicators by themes.';


-- indicator.created_at
COMMENT ON COLUMN gobs.indicator.created_at IS 'Creation timestamp';


-- indicator.updated_at
COMMENT ON COLUMN gobs.indicator.updated_at IS 'Last updated timestamp';


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


-- observation.ob_start_timestamp
COMMENT ON COLUMN gobs.observation.ob_start_timestamp IS 'Start timestamp of the observation data';


-- observation.ob_validation
COMMENT ON COLUMN gobs.observation.ob_validation IS 'Date and time when the data has been validated (the corresponding import status has been changed from pending to validated). Can be used to find all observations not yet validated, with NULL values in this field.';


-- observation.ob_end_timestamp
COMMENT ON COLUMN gobs.observation.ob_end_timestamp IS 'End timestamp of the observation data (optional)';


-- observation.ob_uid
COMMENT ON COLUMN gobs.observation.ob_uid IS 'Observation uid: autogenerated unique identifier';


-- observation.created_at
COMMENT ON COLUMN gobs.observation.created_at IS 'Creation timestamp';


-- observation.updated_at
COMMENT ON COLUMN gobs.observation.updated_at IS 'Last updated timestamp';


-- project
COMMENT ON TABLE gobs.project IS 'List of projects, which represents a group of indicators';


-- project.id
COMMENT ON COLUMN gobs.project.id IS 'Unique identifier';


-- project.pt_code
COMMENT ON COLUMN gobs.project.pt_code IS 'Project code. Ex: weather_data';


-- project.pt_lizmap_project_key
COMMENT ON COLUMN gobs.project.pt_lizmap_project_key IS 'Lizmap project unique identifier (optional): repository_code~project_file_name. Ex: environment~weather';


-- project.pt_label
COMMENT ON COLUMN gobs.project.pt_label IS 'Human readable label of the project. Ex: Weather data publication';


-- project.pt_description
COMMENT ON COLUMN gobs.project.pt_description IS 'Description of the project.';


-- project.pt_indicator_codes
COMMENT ON COLUMN gobs.project.pt_indicator_codes IS 'List of indicator codes available for this project';


-- project.pt_groups
COMMENT ON COLUMN gobs.project.pt_groups IS 'List of groups of users which have access to the project and its indicators, separated by coma.';


-- project.pt_xmin
COMMENT ON COLUMN gobs.project.pt_xmin IS 'Minimum longitude (X min) in EPSG:4326';


-- project.pt_ymin
COMMENT ON COLUMN gobs.project.pt_ymin IS 'Minimum latitude (Y min) in EPSG:4326';


-- project.pt_xmax
COMMENT ON COLUMN gobs.project.pt_xmax IS 'Maximum longitude (X max) in EPSG:4326';


-- project.pt_ymax
COMMENT ON COLUMN gobs.project.pt_ymax IS 'Maximum latitude (Y max) in EPSG:4326';


-- project_view
COMMENT ON TABLE gobs.project_view IS 'Allow to filter the access on projects and relative data (indicators, observations, etc.) with a spatial object for a given list of user groups';


-- project_view.id
COMMENT ON COLUMN gobs.project_view.id IS 'Unique identifier';


-- project_view.pv_label
COMMENT ON COLUMN gobs.project_view.pv_label IS 'Label of the project view';


-- project_view.fk_id_project
COMMENT ON COLUMN gobs.project_view.fk_id_project IS 'Project id (foreign key)';


-- project_view.pv_groups
COMMENT ON COLUMN gobs.project_view.pv_groups IS 'List of user groups allowed to see observation data inside this project view spatial layer object. Use a coma separated value. Ex: "group_a, group_b"';


-- project_view.fk_id_spatial_layer
COMMENT ON COLUMN gobs.project_view.fk_id_spatial_layer IS 'Spatial layer id (foreign key)';


-- project_view.fk_so_unique_id
COMMENT ON COLUMN gobs.project_view.fk_so_unique_id IS 'Spatial object unique id (foreign key). Ex: AB1234. This references the object unique code, not the object integer id field';


-- protocol
COMMENT ON TABLE gobs.protocol IS 'List of protocols';


-- protocol.id
COMMENT ON COLUMN gobs.protocol.id IS 'ID';


-- protocol.pr_code
COMMENT ON COLUMN gobs.protocol.pr_code IS 'Code';


-- protocol.pr_label
COMMENT ON COLUMN gobs.protocol.pr_label IS 'Name of the indicator';


-- protocol.pr_description
COMMENT ON COLUMN gobs.protocol.pr_description IS 'Description, including URLs to references and authors.';


-- r_graph_edge
COMMENT ON TABLE gobs.r_graph_edge IS 'Graph edges: relations between nodes';


-- r_graph_edge.ge_parent_node
COMMENT ON COLUMN gobs.r_graph_edge.ge_parent_node IS 'Parent node';


-- r_graph_edge.ge_child_node
COMMENT ON COLUMN gobs.r_graph_edge.ge_child_node IS 'Child node';


-- r_indicator_node
COMMENT ON TABLE gobs.r_indicator_node IS 'Pivot table between indicators and nodes';


-- r_indicator_node.fk_id_indicator
COMMENT ON COLUMN gobs.r_indicator_node.fk_id_indicator IS 'Parent indicator';


-- r_indicator_node.fk_id_node
COMMENT ON COLUMN gobs.r_indicator_node.fk_id_node IS 'Parent node';


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


-- spatial_object.so_valid_from
COMMENT ON COLUMN gobs.spatial_object.so_valid_from IS 'Date from which the spatial object is valid.';


-- spatial_object.so_valid_to
COMMENT ON COLUMN gobs.spatial_object.so_valid_to IS 'Date from which the spatial object is not valid. Optional: if not given, the spatial object is always valid';


-- spatial_object.so_uid
COMMENT ON COLUMN gobs.spatial_object.so_uid IS 'Spatial object uid: autogenerated unique identifier';


-- spatial_object.created_at
COMMENT ON COLUMN gobs.spatial_object.created_at IS 'Creation timestamp';


-- spatial_object.updated_at
COMMENT ON COLUMN gobs.spatial_object.updated_at IS 'Last updated timestamp';


--
-- PostgreSQL database dump complete
--

