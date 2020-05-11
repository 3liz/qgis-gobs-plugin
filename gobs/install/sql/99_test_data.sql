-- TABLES
-- actor_category
INSERT INTO gobs.actor_category (id, ac_label, ac_description) VALUES (1, 'Public organizations', '');
INSERT INTO gobs.actor_category (id, ac_label, ac_description) VALUES (2, 'Research centers', '');

-- actor
INSERT INTO gobs.actor (id, a_label, a_description, a_email, id_category) VALUES (1, 'IGN', 'French national geographical institute.', 'contact@ign.fr', 1);
INSERT INTO gobs.actor (id, a_label, a_description, a_email, id_category) VALUES (2, 'CIRAD', 'The French agricultural research and international cooperation organization working for the sustainable development of tropical and Mediterranean regions.

https://www.cirad.fr/en/home-page', 'contact@cirad.fr', 2);
INSERT INTO gobs.actor (id, a_label, a_description, a_email, id_category) VALUES (3, 'DREAL Bretagne', 'Direction régionale de l''environnement, de l''aménagement et du logement, région Bretagne.', 'email@dreal.fr', 1);

-- indicator
INSERT INTO gobs.indicator (id, id_code, id_label, id_description, id_date_format, id_value_code, id_value_name, id_value_type, id_value_unit, id_paths)
VALUES (1, 'pluviometry', 'Hourly pluviometry ', 'Hourly rainfall pluviometry in millimetre', 'hour', '{pluviometry}', '{Pluviometry}', '{real}', '{mm}', 'Environment / Water / Data | Physical and chemical conditions / Water ');
INSERT INTO gobs.indicator (id, id_code, id_label, id_description, id_date_format, id_value_code, id_value_name, id_value_type, id_value_unit, id_paths)
VALUES (2, 'population', 'Population ', 'Number of inhabitants for city', 'year', '{population}', '{Population}', '{integer}', '{people}', 'Socio-eco / Demography / Population ');

-- protocol
INSERT INTO gobs.protocol (id, pr_code, pr_label, pr_description) VALUES (1, 'cirad-pluviometry', 'Pluviometry', 'Measure of rainfall in mm');
INSERT INTO gobs.protocol (id, pr_code, pr_label, pr_description) VALUES (2, 'cirad-population', 'Population', 'Number of inhabitants obtained from census.');

-- spatial_layer
INSERT INTO gobs.spatial_layer (id, sl_code, sl_label, sl_description, sl_creation_date, fk_id_actor, sl_geometry_type) VALUES (1, 'pluviometers', 'Pluviometers', 'Sites equiped with pluviometers to measure rainfalls', '2019-06-26', 2, 'point');
INSERT INTO gobs.spatial_layer (id, sl_code, sl_label, sl_description, sl_creation_date, fk_id_actor, sl_geometry_type) VALUES (2, 'brittany-cities', 'Cities of Brittany , France', 'Cities of Brittany, France', '2019-07-05', 2, 'multipolygon');

-- series
INSERT INTO gobs.series (id, fk_id_protocol, fk_id_actor, fk_id_indicator, fk_id_spatial_layer) VALUES (1, 1, 2, 1, 1);
INSERT INTO gobs.series (id, fk_id_protocol, fk_id_actor, fk_id_indicator, fk_id_spatial_layer) VALUES (2, 2, 2, 2, 2);

-- SEQUENCES
SELECT pg_catalog.setval('gobs.actor_category_id_seq', 3, true);
SELECT pg_catalog.setval('gobs.actor_id_seq', 3, true);
SELECT pg_catalog.setval('gobs.indicator_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.protocol_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.spatial_layer_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.series_id_seq', 2, true);

