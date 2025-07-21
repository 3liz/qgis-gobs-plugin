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

-- im_status
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('im_status', 'P', 'Pending validation', 'Data has been imported but not yet validated by its owner', 1);
INSERT INTO glossary (gl_field, gl_code, gl_label, gl_description, gl_order) VALUES ('im_status', 'V', 'Validated data', 'Data has been validated and is visible to more users depending on their granted access', 2);

-- Add actor categories
INSERT INTO gobs.actor_category
(id, ac_label, ac_description)
VALUES
(1, 'other', 'Other actors'),
(2, 'platform_user', 'Platform users')
ON CONFLICT DO NOTHING
;

-- Add default project and project view
-- Add a default project if no project can be found
INSERT INTO gobs.project
(pt_code, pt_lizmap_project_key, pt_label, pt_description)
SELECT
'default_project', NULL, 'Default G-Obs project', 'This project can be used to group series.'
WHERE NOT EXISTS (
    SELECT id
    FROM gobs.project
    WHERE pt_code = 'default_project'
)
ON CONFLICT DO NOTHING
;
-- Default project view
INSERT INTO gobs.project_view
(pv_type, pv_label, pv_groups, fk_id_project, geom)
SELECT
    'global',
    'Defaut global view',
    'admins, group_a, group_b',
    (SELECT id FROM gobs.project WHERE pt_code = 'default_project'),
    public.ST_MakeEnvelope(-180, -90, 180, 90, 4326)
WHERE NOT EXISTS (
    SELECT id
    FROM gobs.project_view
    WHERE fk_id_project = (
        SELECT id
        FROM gobs.project
        WHERE pt_code = 'default_project'
    )
    AND pv_type = 'global'
)
ON CONFLICT DO NOTHING
;
