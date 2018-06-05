DROP FUNCTION geoobs.get_geom_by_geom_data(text);
CREATE OR REPLACE FUNCTION geoobs.get_geom_by_geom_data (geomSource text)
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
    FROM geoobs.spatial_object so, geoobs.data d, geoobs.indicator i
    WHERE 
     ST_intersects(so.geom, ST_SetSRID(ST_geomFromText(geomSource),4326))
	 AND i.id = d.fk_id_indicator
	 AND d.fk_id_spatial_object = so.so_id_given_by_source::integer;
END; $$
 
LANGUAGE 'plpgsql';

DROP FUNCTION geoobs.get_geom_by_geom(text);
CREATE OR REPLACE FUNCTION geoobs.get_geom_by_geom (geomSource text)
 RETURNS TABLE (
 id integer,
 fk_id_spatial_layer integer,
 fk_id_spatial_object integer,
 geom geometry
)
AS $$
BEGIN
 RETURN QUERY SELECT so.id, so.fk_id_spatial_layer, so.so_id_given_by_source::integer, so.geom
    FROM geoobs.spatial_object so
    WHERE ST_intersects(so.geom, ST_SetSRID(ST_geomFromText(geomSource),4326));
END; $$
 
LANGUAGE 'plpgsql';