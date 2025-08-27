
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
