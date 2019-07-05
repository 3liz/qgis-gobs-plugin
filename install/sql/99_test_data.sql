-- TABLES
-- actor_category
INSERT INTO gobs.actor_category (id, ac_name, ac_description) VALUES (1, 'Public organizations', '');
INSERT INTO gobs.actor_category (id, ac_name, ac_description) VALUES (2, 'Research centers', '');

-- actor
INSERT INTO gobs.actor (id, a_name, a_description, a_email, id_category) VALUES (1, 'IGN', 'French national geographical institute.', 'contact@ign.fr', 1);
INSERT INTO gobs.actor (id, a_name, a_description, a_email, id_category) VALUES (2, 'CIRAD', 'The French agricultural research and international cooperation organization working for the sustainable development of tropical and Mediterranean regions.

https://www.cirad.fr/en/home-page', 'contact@cirad.fr', 2);

-- indicator
INSERT INTO gobs.indicator (id, id_label, id_title, id_description, id_date_format, id_value_code, id_value_name, id_value_type, id_value_unit) VALUES (1, 'pluviometry', 'Daily pluviometry ', 'Daily rainfall pluviometry in millimetre', 'day', '{pluviometry}', '{Pluviometry}', 'integer', 'mm');

-- protocol
INSERT INTO gobs.protocol (id, pr_code, pr_name, pr_description) VALUES (1, 'cirad-pluviometry', 'Pluviometry', 'Measure of rainfall in mm
Material : ...');


-- spatial_layer
INSERT INTO gobs.spatial_layer (id, sl_code, sl_label, sl_description, sl_creation_date, fk_id_actor, sl_geometry_type) VALUES (1, 'pluviometers', 'Pluviometers', 'Sites equiped with pluviometers to mesure rainfalls', '2019-06-26', 2, 'point');
INSERT INTO gobs.spatial_layer (id, sl_code, sl_label, sl_description, sl_creation_date, fk_id_actor, sl_geometry_type) VALUES (2, 'montpellier-districts', 'Montpellier districts', 'Districts of Montpellier, France', '2019-07-05', 2, 'multipolygon');


-- SEQUENCES
SELECT pg_catalog.setval('gobs.actor_category_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.actor_id_seq', 2, true);
SELECT pg_catalog.setval('gobs.indicator_id_seq', 1, true);
SELECT pg_catalog.setval('gobs.protocol_id_seq', 1, true);
SELECT pg_catalog.setval('gobs.spatial_layer_id_seq', 2, true);

