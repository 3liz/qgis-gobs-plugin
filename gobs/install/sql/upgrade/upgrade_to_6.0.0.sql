-- Update project and project view

-- Create a new table to store the indicator dimensions
CREATE TABLE IF NOT EXISTS gobs.dimension (
    id serial NOT NULL PRIMARY KEY,
    fk_id_indicator integer NOT NULL,
    di_code text NOT NULL,
    di_label text NOT NULL,
    di_type text NOT NULL,
    di_unit text
);

COMMENT ON TABLE gobs.dimension
IS 'Stores the different dimensions characteristics of an indicator'
;

COMMENT ON COLUMN gobs.dimension.fk_id_indicator IS 'Id of the corresponding indicator.';
COMMENT ON COLUMN gobs.dimension.di_code IS 'Code of the vector dimension. Ex: ''pop_h'' or ''pop_f''';
COMMENT ON COLUMN gobs.dimension.di_label IS 'Label of the vector dimensions. Ex: ''population homme'' or ''population femme''';
COMMENT ON COLUMN gobs.dimension.di_type IS 'Type of the stored values. Ex: ''integer'' or ''real''';
COMMENT ON COLUMN gobs.dimension.di_unit IS 'Unit ot the store values. Ex: ''inhabitants'' or ''°C''';


-- Foreign key constraint to indicator
ALTER TABLE gobs.dimension
ADD CONSTRAINT dimension_fk_id_indicator_fkey FOREIGN KEY (fk_id_indicator) REFERENCES gobs.indicator(id)
;

-- Unique constraint
ALTER TABLE gobs.dimension
ADD UNIQUE (fk_id_indicator, di_code);

-- Insert data from current indicators
INSERT INTO gobs.dimension (fk_id_indicator, di_code, di_label, di_type, di_unit)
WITH source AS (
	SELECT
		id, id_value_code, id_value_name, id_value_type, id_value_unit,
		generate_series(1, array_length(id_value_code, 1)) AS idx
	FROM gobs.indicator
	WHERE id_value_code IS NOT NULL
)
SELECT
	id AS fk_id_indicator,
	Coalesce(id_value_code[idx], '-') AS di_code,
	Coalesce(id_value_name[idx], '-') AS di_label,
	Coalesce(id_value_type[idx], 'text') AS di_type,
	Coalesce(id_value_unit[idx], '') AS di_unit
FROM source
WHERE TRUE
ON CONFLICT ON CONSTRAINT dimension_fk_id_indicator_di_code_key
DO NOTHING
;

-- Remove the fields
ALTER TABLE gobs.indicator DROP COLUMN id_value_code;
ALTER TABLE gobs.indicator DROP COLUMN id_value_name;
ALTER TABLE gobs.indicator DROP COLUMN id_value_type;
ALTER TABLE gobs.indicator DROP COLUMN id_value_unit;
