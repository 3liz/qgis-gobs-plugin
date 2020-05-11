-- delete useless tables
DROP TABLE IF EXISTS gobs.qgisproject CASCADE;
DROP TABLE IF EXISTS gobs.r_qgisproject_node CASCADE;

-- Use a table for id_value_type and id_value_unit
ALTER TABLE gobs.indicator ALTER COLUMN id_value_type DROP DEFAULT;

ALTER TABLE gobs.indicator ALTER COLUMN id_value_type SET DATA TYPE text[] USING (string_to_array(trim(repeat(concat(id_value_type, ','), array_length(id_value_code,1)), ','), ','))::text[];
ALTER TABLE gobs.indicator ALTER COLUMN id_value_unit SET DATA TYPE text[] USING (string_to_array(trim(repeat(concat(id_value_unit, ','), array_length(id_value_code,1)), ','), ','))::text[];
