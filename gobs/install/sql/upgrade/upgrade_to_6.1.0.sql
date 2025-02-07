-- Update project and project view

-- project: remove the useless fields
ALTER TABLE gobs.project DROP COLUMN IF EXISTS pt_xmin;
ALTER TABLE gobs.project DROP COLUMN IF EXISTS pt_ymin;
ALTER TABLE gobs.project DROP COLUMN IF EXISTS pt_xmax;
ALTER TABLE gobs.project DROP COLUMN IF EXISTS pt_ymax;
ALTER TABLE gobs.project DROP COLUMN IF EXISTS pt_groups;

-- project_view
-- comment
COMMENT ON TABLE gobs.project_view
IS 'Allow to filter the access on projects and relative data (indicators, observations, etc.) with a spatial object for a given list of user groups.
There must be at least one project view for the project, of type global. The other views must be of type filter.';

-- delete useless columns
ALTER TABLE gobs.project_view DROP COLUMN IF EXISTS fk_id_spatial_layer;
ALTER TABLE gobs.project_view DROP COLUMN IF EXISTS fk_so_unique_id;

-- pv_type
ALTER TABLE gobs.project_view ADD COLUMN IF NOT EXISTS "pv_type" text NOT NULL DEFAULT 'global';
COMMENT ON COLUMN gobs.project_view.pv_type
IS 'Type of the project view : "global" for the unique global view, and "filter" for the view made for spatial filter purpose';

ALTER TABLE gobs.project_view ADD COLUMN IF NOT EXISTS "geom" public.geometry(MULTIPOLYGON, 4326) NOT NULL;
COMMENT ON COLUMN gobs.project_view.geom
IS 'Geometry of the project view: no observation can be created outside the project views geometries accessible from the authenticated user.';


-- Replace bigint data type by simple integer
ALTER TABLE gobs.spatial_object ALTER COLUMN id SET DATA TYPE integer USING id::integer;
ALTER TABLE gobs.observation ALTER COLUMN id SET DATA TYPE integer USING id::integer;
ALTER TABLE gobs.observation ALTER COLUMN fk_id_spatial_object SET DATA TYPE integer USING fk_id_spatial_object::integer;

-- Glossary
ALTER TABLE gobs.glossary ADD UNIQUE (gl_field, gl_code);
INSERT INTO gobs.glossary
(gl_field, gl_code, gl_label, gl_description, gl_order)
VALUES
('pv_type', 'global', 'Global', 'Global project view (only one per project)', 1),
('pv_type', 'filter', 'Filter', 'Filter view (to restrict access to some observations)', 2)
ON CONFLICT DO NOTHING
;
ALTER TABLE gobs.glossary DROP CONSTRAINT IF EXISTS glossary_gl_field_gl_code_key;
