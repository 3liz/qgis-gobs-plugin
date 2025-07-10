BEGIN;

-- TABLES
-- actor_category
INSERT INTO gobs.actor_category
(id, ac_label, ac_description)
VALUES
(1, 'other', 'Other actors'),
(2, 'platform_user', 'Platform users')
;

-- actor
INSERT INTO gobs.actor
(id, a_label, a_description, a_email, id_category)
VALUES
(1, 'IGN', 'French national geographical institute.', 'contact@ign.fr', 1),
(2, 'CIRAD', 'The French agricultural research and international cooperation organization', 'contact@cirad.fr', 1),
(3, 'DREAL Bretagne', 'Direction régionale de l''environnement, de l''aménagement et du logement.', 'email@dreal.fr', 1),
(4, 'Al', 'Al A.', 'al@al.al', 1),
(5, 'Bob', 'Bob B.', 'bob@bob.bob', 1),
(6, 'John', 'John J.', 'jon@jon.jon', 1),
(7, 'Mike', 'Mike M.', 'mik@mik.mik', 1),
(8, 'Phil', 'Phil P.', 'phi@phi.phi', 1)
;

-- indicator
INSERT INTO gobs.indicator
(id, id_code, id_label, id_description, id_date_format, id_paths, id_category)
VALUES
(1, 'pluviometry', 'Hourly pluviometry ', 'Hourly rainfall pluviometry in millimetre', 'hour', 'Environment / Water / Data | Physical and chemical conditions / Water ', 'Water'),
(2, 'population', 'Population ', 'Number of inhabitants for city', 'year', 'Socio-eco / Demography / Population ', 'Population'),
(3, 'hiker_position', 'Hikers position', 'Position and altitude of hikers', 'second', 'Hiking / Tracks', 'Tracks'),
(4, 'observation', 'Observations', 'Faunal observations in the field', 'second', 'Environment / Fauna / Species', 'Species')
;

-- dimension
INSERT INTO gobs.dimension
(id, fk_id_indicator, di_code, di_label, di_type, di_unit)
VALUES
(1, 1, 'pluviometry', 'Pluviometry', 'real', 'mm'),
(2, 2, 'population', 'Population', 'integer', 'people'),
(3, 3, 'altitude', 'Altitude', 'integer', 'm'),
(4, 4, 'number', 'Number of individuals', 'integer', 'ind'),
(5, 4, 'species', 'Observed species', 'text', 'sp')
;

-- document
INSERT INTO gobs.document VALUES
(1, '542aa72f-d1de-4810-97bb-208f2388698b', 'Illustration', 'Picture to use as the indicator illustration.', 'preview', 'hiker_position/preview/hiking.jpg', 3, '2022-10-11 08:30:18.012801', '2022-10-11 08:50:01.248526'),
(2, '1a7f7323-6b18-46ed-a9fe-9efbe1f006a2', 'Hiking presentation', 'Presentation of hiking.', 'document', 'hiker_position/document/hiking_doc.txt', 3, '2022-10-11 08:30:18.012801', '2022-10-11 08:50:01.248526')
;

-- protocol
INSERT INTO gobs.protocol
(id, pr_code, pr_label, pr_description)
VALUES
(1, 'pluviometry', 'Pluviometry', 'Measure of rainfall in mm'),
(2, 'population', 'Population', 'Number of inhabitants obtained from census.'),
(3, 'gps-tracking', 'GPS tracking', 'GPS position recorded by a smartphone containing timestamp at second resolution, position and altitude in meters.'),
(4, 'field_observations', 'Field observations on species', 'Go to the field, recognize the observed species and give the number of individuals.')
;

-- spatial_layer
INSERT INTO gobs.spatial_layer
(id, sl_code, sl_label, sl_description, sl_creation_date, sl_geometry_type)
VALUES
(1, 'pluviometers', 'Pluviometers', 'Sites equiped with pluviometers to measure rainfalls', '2019-06-26', 'point'),
(2, 'brittany-cities', 'Cities of Brittany , France', 'Cities of Brittany, France', '2019-07-05', 'multipolygon'),
(3, 'gpsposition', 'GPS position', 'Position of GPS trackers', '2020-09-10', 'point'),
(4, 'faunal_observation', 'Position of faunal observations', 'Observations on species (lions, girafes, etc.)', '2022-09-10', 'point')
;

-- projects
INSERT INTO gobs.project
(id, pt_code, pt_lizmap_project_key, pt_label, pt_description)
VALUES
(1, 'test_project_a', NULL, 'GobsAPI test project a', 'Test project a')
;

-- project_view
INSERT INTO gobs.project_view
(id, pv_label, fk_id_project, pv_groups, pv_type, geom)
VALUES
(2, 'Test project a filtered view', 1, 'gobsapi_filtered_group', 'filter', '0106000020E610000001000000010300000001000000050000002ABFB10C16030FC00B560706313248402ABFB10C16030FC06ED711A8FA4148408B7248EED9680DC06ED711A8FA4148408B7248EED9680DC00B560706313248402ABFB10C16030FC00B56070631324840'),
(1, 'Test project a global view', 1, 'gobsapi_global_group', 'global', '0106000020E61000000100000001030000000100000005000000FD41B0EC7A980FC02757CA956E2B4840FD41B0EC7A980FC0FA9B7196694948403511B20319CF0CC0FA9B7196694948403511B20319CF0CC02757CA956E2B4840FD41B0EC7A980FC02757CA956E2B4840')
;

-- series
INSERT INTO gobs.series
(id, fk_id_protocol, fk_id_indicator, fk_id_spatial_layer, fk_id_project)
VALUES
(1, 1, 1, 1, 1),
(2, 2, 2, 2, 1),
(3, 3, 3, 3, 1),
(4, 3, 3, 3, 1),
(5, 3, 3, 3, 1),
(6, 3, 3, 3, 1),
(7, 3, 3, 3, 1),
(8, 4, 4, 4, 1)
;

-- SEQUENCES
SELECT pg_catalog.setval('gobs.actor_category_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.actor_id_seq', 8, true);
SELECT pg_catalog.setval('gobs.indicator_id_seq', 4, true);
SELECT pg_catalog.setval('gobs.dimension_id_seq', 5, true);
SELECT pg_catalog.setval('gobs.document_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.protocol_id_seq', 4, true);
SELECT pg_catalog.setval('gobs.spatial_layer_id_seq', 4, true);
SELECT pg_catalog.setval('gobs.project_id_seq', 1, true);
SELECT pg_catalog.setval('gobs.project_view_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.series_id_seq', 8, true);

COMMIT;
