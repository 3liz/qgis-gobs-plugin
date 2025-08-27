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
;
