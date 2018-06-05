DROP FUNCTION geoobs.get_geom_by_id_indicator(numeric);
CREATE OR REPLACE FUNCTION geoobs.get_geom_by_id_indicator (id_indicator NUMERIC)
 RETURNS TABLE (
 id integer,
 fk_id_spatial_object integer,
 d_vector jsonb,
 d_timestamp timestamp,
 i_type text
)
AS $$
BEGIN
 RETURN QUERY SELECT d.id, d.fk_id_spatial_object, d.d_vector, d.d_timestamp, i.i_type
    FROM  geoobs.data d, geoobs.spatial_layer sl, geoobs.indicator i
    WHERE  
    d.fk_id_spatial_layer = sl.id
    AND d.fk_id_indicator = i.id
    AND d.fk_id_indicator = id_indicator;
END; $$
 
LANGUAGE 'plpgsql';

DROP FUNCTION geoobs.get_geom_by_id_indicator_geom(numeric);
CREATE OR REPLACE FUNCTION geoobs.get_geom_by_id_indicator_geom (id_indicator NUMERIC)
 RETURNS TABLE (
 id integer,
 fk_id_spatial_object integer,
 geom geometry
)
AS $$
BEGIN
 RETURN QUERY 
    SELECT so.id, so.so_id_given_by_source::integer, so.geom
    FROM geoobs.spatial_object so
    WHERE  
    so.fk_id_spatial_layer = (
        SELECT fk_id_spatial_layer
        FROM geoobs.data d
        WHERE True
        AND fk_id_indicator = id_indicator
        LIMIT 1
    );
END; $$
 
LANGUAGE 'plpgsql';