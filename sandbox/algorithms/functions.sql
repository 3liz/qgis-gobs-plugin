##cirad=group
##01 Generate functions=name
##Service_PostgreSQL=string cirad_project

import psycopg2
from PyQt4.QtSql import *
from qgis.PyQt.QtCore import *
from qgis.core import *
from qgis.utils import *
import processing

sql='''
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

DROP FUNCTION geoobs.get_geom_by_time(timestamp, timestamp);
CREATE OR REPLACE FUNCTION geoobs.get_geom_by_time (date_start timestamp, date_end timestamp)
 RETURNS TABLE (
 id integer,
 so_id_given_by_source text,
 d_vector jsonb,
 d_timestamp timestamp,
 i_type text,
 geom geometry
)
AS $$
BEGIN
 RETURN QUERY SELECT d.id, so.so_id_given_by_source, d.d_vector, d.d_timestamp, i.i_type, so.geom
    FROM geoobs.spatial_object so, geoobs.data d, geoobs.spatial_layer sl, geoobs.indicator i
    WHERE  
     so.id = d.fk_id_spatial_object
    AND d.fk_id_spatial_layer = sl.id
    AND d.fk_id_indicator = i.id
    AND d.d_timestamp > date_start
    AND d.d_timestamp < date_end;
END; $$
 
LANGUAGE 'plpgsql';

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

'''
#The script to create the function
conversion = processing.runalg(
    'script:executepostgissqlonservicedatabase',
    'cirad_project',
    sql
)
