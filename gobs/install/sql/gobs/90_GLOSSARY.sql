--
-- PostgreSQL database dump
--

-- Dumped from database version 13.7 (Debian 13.7-1.pgdg110+1)
-- Dumped by pg_dump version 13.7 (Debian 13.7-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: glossary; Type: TABLE DATA; Schema: gobs; Owner: -
--

INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (1, 'id_date_format', 'second', 'Second', 'Second resolution', 1);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (2, 'id_date_format', 'minute', 'Minute', 'Minute resolution', 2);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (3, 'id_date_format', 'hour', 'Hour', 'Hour resolution', 3);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (4, 'id_date_format', 'day', 'Day', 'Day resolution', 4);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (5, 'id_date_format', 'month', 'Month', 'Month resolution', 5);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (6, 'id_date_format', 'year', 'Year', 'Year resolution', 6);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (7, 'id_value_type', 'integer', 'Integer', 'Integer', 1);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (8, 'id_value_type', 'real', 'Real', 'Real', 2);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (9, 'id_value_type', 'text', 'Text', 'Text', 3);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (10, 'id_value_type', 'date', 'Date', 'Date', 4);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (11, 'id_value_type', 'timestamp', 'Timestamp', 'Timestamp', 5);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (12, 'id_value_type', 'boolean', 'Boolean', 'Boolean', 6);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (13, 'sl_geometry_type', 'point', 'Point', 'Simple point geometry', 1);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (14, 'sl_geometry_type', 'multipoint', 'MultiPoint', 'Multi point geometry', 2);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (15, 'sl_geometry_type', 'linestring', 'Linestring', 'Simple linestring geometry', 3);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (16, 'sl_geometry_type', 'multilinestring', 'MultiLinestring', 'Multi linestring geometry', 4);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (17, 'sl_geometry_type', 'polygon', 'Polygon', 'Simple polygon', 5);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (18, 'sl_geometry_type', 'multipolygon', 'MultiPolygon', 'Multi Polygon geometry', 6);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (19, 'im_status', 'P', 'Pending validation', 'Data has been imported but not yet validated by its owner', 1);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (20, 'im_status', 'V', 'Validated data', 'Data has been validated and is visible to more users depending on their granted access', 2);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (21, 'do_type', 'preview', 'Preview', 'Preview is an image defining the indicator', 1);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (22, 'do_type', 'image', 'Image', 'Image', 2);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (23, 'do_type', 'video', 'Video', 'Video', 3);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (24, 'do_type', 'document', 'Document', 'Generic document like PDF, ODT, text files or archives', 4);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (25, 'do_type', 'url', 'URL', 'URL pointing to the document', 5);
INSERT INTO gobs.glossary (id, gl_field, gl_code, gl_label, gl_description, gl_order) VALUES (26, 'do_type', 'other', 'Other', 'Other type of document', 6);


--
-- Name: glossary_id_seq; Type: SEQUENCE SET; Schema: gobs; Owner: -
--

SELECT pg_catalog.setval('gobs.glossary_id_seq', 26, true);


--
-- PostgreSQL database dump complete
--

