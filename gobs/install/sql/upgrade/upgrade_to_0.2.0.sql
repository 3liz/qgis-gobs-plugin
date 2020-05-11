-- Store QGIS project references
CREATE TABLE IF NOT EXISTS gobs.qgisproject (
    id serial primary key,
    qp_project text NOT NULL,
    qp_repository text NOT NULL,
    qp_paths text
);


ALTER TABLE gobs.qgisproject DROP CONSTRAINT IF EXISTS qgisproject_qp_project_qp_repository_key;
ALTER TABLE gobs.qgisproject ADD UNIQUE (qp_project, qp_repository);

COMMENT ON TABLE gobs.qgisproject IS 'Store references of QGIS projects. Each project has one or many nodes';
COMMENT ON COLUMN gobs.qgisproject.id IS 'Unique automatic id (serial)';
COMMENT ON COLUMN gobs.qgisproject.qp_project IS 'QGIS Project name, which is the name of the *.qgs file without the extension';
COMMENT ON COLUMN gobs.qgisproject.qp_repository IS 'Lizmap repository name, which is the ID of Lizmap repository configured in the Lizmap admin panel';
COMMENT ON COLUMN gobs.qgisproject.qp_paths IS 'Paths given to help finding a QGIS project. They will be split up to fill the graph_node and r_qgisproject_node tables. If you need multiple paths, use | as a separator. Ex: Environment / Water resources | Measure / Physics / Water';

-- Store links between nodes and QGIS project
CREATE TABLE IF NOT EXISTS gobs.r_qgisproject_node (
    fk_id_qgisproject integer,
    fk_id_node integer
);


ALTER TABLE gobs.r_qgisproject_node DROP CONSTRAINT IF EXISTS r_qgisproject_node_pkey;
ALTER TABLE gobs.r_qgisproject_node ADD PRIMARY KEY (fk_id_qgisproject, fk_id_node);

COMMENT ON TABLE gobs.r_qgisproject_node IS 'Pivot table between the QGIS projects and the thematic nodes.';
COMMENT ON COLUMN gobs.r_qgisproject_node.fk_id_qgisproject IS 'Id of the QGIS project';
COMMENT ON COLUMN gobs.r_qgisproject_node.fk_id_node IS 'Id of the node';

ALTER TABLE gobs.r_qgisproject_node
DROP CONSTRAINT IF EXISTS r_qgisproject_node_fk_id_qgisproject_fkey;
ALTER TABLE gobs.r_qgisproject_node
ADD CONSTRAINT r_qgisproject_node_fk_id_qgisproject_fkey
FOREIGN KEY (fk_id_qgisproject) REFERENCES gobs.qgisproject(id)
ON DELETE CASCADE;

ALTER TABLE gobs.r_qgisproject_node
DROP CONSTRAINT IF EXISTS r_qgisproject_node_fk_id_node_fkey;
ALTER TABLE gobs.r_qgisproject_node
ADD CONSTRAINT r_qgisproject_node_fk_id_node_fkey
FOREIGN KEY (fk_id_node) REFERENCES gobs.graph_node(id)
ON DELETE CASCADE;
