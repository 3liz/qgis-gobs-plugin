DROP FUNCTION geoobs.get_geom_by_id_indicator_and_time (NUMERIC, timestamp, timestamp);
CREATE OR REPLACE FUNCTION geoobs.get_geom_by_id_indicator_and_time (id_indicator NUMERIC, date_start timestamp, date_end timestamp)
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
    AND d.fk_id_indicator = id_indicator
    AND d.d_timestamp > date_start
    AND d.d_timestamp < date_end;
END; $$
 
LANGUAGE 'plpgsql';

DROP FUNCTION geoobs.get_geom_by_id_indicator_and_time_geom (NUMERIC, timestamp, timestamp);
CREATE OR REPLACE FUNCTION geoobs.get_geom_by_id_indicator_and_time_geom (id_indicator NUMERIC, date_start timestamp, date_end timestamp)
 RETURNS TABLE (
 id integer,
 fk_id_spatial_object integer,
 geom geometry
)
AS $$
BEGIN
RETURN QUERY SELECT  so.id, so.so_id_given_by_source::integer, so.geom
    FROM geoobs.spatial_object so, geoobs.data d
    WHERE  
    so.fk_id_spatial_layer = (
        SELECT fk_id_spatial_layer
        FROM geoobs.data
        WHERE True
        AND fk_id_indicator = id_indicator
        LIMIT 1
    )
    AND so.fk_id_spatial_layer = d.fk_id_spatial_layer
    AND d.d_timestamp > date_start
    AND d.d_timestamp < date_end;
END; $$
 
LANGUAGE 'plpgsql';