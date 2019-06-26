SET search_path TO gobs,public;

-- indicator
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_date_format', 'second', 'Second', 'Second resolution', 1);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_date_format', 'minute', 'Minute', 'Minute resolution', 2);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_date_format', 'hour', 'Hour', 'Hour resolution', 3);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_date_format', 'day', 'Day', 'Day resolution', 4);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_date_format', 'month', 'Month', 'Month resolution', 5);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_date_format', 'year', 'Year', 'Year resolution', 6);

-- id_value_type
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_value_type', 'integer', 'Integer', 'Integer', 1);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_value_type', 'real', 'Real', 'Real', 2);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_value_type', 'text', 'Text', 'Text', 3);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_value_type', 'date', 'Date', 'Date', 4);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_value_type', 'timestamp', 'Timestamp', 'Timestamp', 5);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('id_value_type', 'boolean', 'Boolean', 'Boolean', 6);

-- sl_geometry_type
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('sl_geometry_type', 'point', 'Point', 'Simple point geometry', 1);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('sl_geometry_type', 'multipoint', 'MultiPoint', 'Multi point geometry', 2);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('sl_geometry_type', 'linestring', 'Linestring', 'Simple linestring geometry', 3);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('sl_geometry_type', 'multilinestring', 'MultiLinestring', 'Multi linestring geometry', 4);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('sl_geometry_type', 'polygon', 'Polygon', 'Simple polygon', 5);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('sl_geometry_type', 'multipolygon', 'MultiPolygon', 'Multi Polygon geometry', 6);
