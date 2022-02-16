##cirad=group
##03 Filter indicator by time_indicator=name
##Service_PostgreSQL=string cirad_project
##Database_type=selection postgis;spatialite
##Database_name=string cirad
##id_indicator=number 
##Starting_date=string YYYY-MM-DD
##Ending_date=string YYYY-MM-DD
##layer_name=string Choose_name

import psycopg2

from db_manager.db_plugins import createDbPlugin
from db_manager.db_plugins.plugin import BaseError, DBPlugin, Schema, Table
from db_manager.dlg_db_error import DlgDbError
from PyQt4.QtSql import *
from qgis.core import *
from qgis.PyQt.QtCore import *
from qgis.utils import *

dbTypeMap = { 0: 'postgis', 1: 'spatialite' }

#Connection and creation of the cursor
dbpluginclass = createDbPlugin( dbTypeMap[Database_type], Database_name )
cnx = dbpluginclass.connect()
db = dbpluginclass.database()
connector = db.connector
cursorVector = connector._get_cursor()

#Request to get the key of the d_vector field and indicator type wo will be used in the function
sqlQueryVector='''
    SELECT jsonb_object_keys(d.d_vector), i.i_type 
    FROM geoobs.indicator i, geoobs.data d 
    WHERE i.id = %i AND i.id = d.fk_id_indicator
    AND d.d_timestamp > ('%s'::timestamp)
    AND d.d_timestamp < ('%s'::timestamp)
    LIMIT 1
    ''' % (
    id_indicator, Starting_date, Ending_date)
    
cursorVector.execute(sqlQueryVector)
   
#field_vector_name = cursorVector.fetchone()[0]

cursorVector.execute(sqlQueryVector)
field_type = cursorVector.fetchone()[1]

cursorVector.close()
del cursorVector

sqlData='''
    SELECT id, fk_id_spatial_object ,
        (d_vector->>jsonb_object_keys(d_vector))::%s as "value",
        d_timestamp
        FROM geoobs.get_geom_by_id_indicator_and_time(%i,'%s'::timestamp,'%s'::timestamp)
''' % (
         field_type, id_indicator, Starting_date, Ending_date )
            
sqlGeom='''
    SELECT * FROM geoobs.get_geom_by_id_indicator_and_time_geom(%i,'%s'::timestamp, '%s'::timestamp) ''' % (id_indicator, Starting_date, Ending_date)
            
progress.setInfo('Service PostgreSQL:')
progress.setInfo(Service_PostgreSQL)
progress.setInfo('SQL:')
progress.setInfo(sqlData)

loadGeom= processing.runalg(
    'script:addvectorlayerfromsqlquery',
    0,
    Database_name,
    sqlGeom,
    sqlData,
    layer_name,
    'geom',
    'id',
    'true'
)

