##cirad=group
##test intersect=name
##layer=vector
##Name_primaryKey_id_or_label=string QUARTMNO (id or field with the name you want)

import processing

from qgis.core import *

geoms = QgsGeometry.fromWkt('GEOMETRYCOLLECTION()')
layer = processing.getObject(layer)
featureCount = layer.featureCount()
cptFeature = 0
sql = ''
sqlData = ''
for feature in layer.getFeatures():
    nameField=feature[Name_pk_label]
    xform = QgsCoordinateTransform(layer.crs(), QgsCoordinateReferenceSystem(4326))
    geoms = feature.geometry()
    geoms.transform(xform)
    geoms = geoms.exportToWkt()
    
    sqlData +='''
        SELECT '%s'::text AS "%s",
            id, fk_id_spatial_object ,
            (d_vector->>jsonb_object_keys(d_vector))::text as "Value_indicator",
            d_timestamp
        FROM  geoobs.get_geom_by_geom_data('%s')
        ''' % (nameField, Name_pk_label, geoms)
        
    sql +='''
        SELECT '%s'::text AS "%s",* from geoobs.get_geom_by_geom('%s')
        ''' %  (nameField, Name_pk_label, geoms)
        
    if( cptFeature< featureCount-1 ):
        sql += ''' 
        UNION ALL
        '''
        sqlData += '''
        UNION ALL
        '''
        cptFeature = cptFeature + 1

progress.setInfo('SQL:')
progress.setInfo(sql)
load = processing.runalg(
    'script:addvectorlayerfromsqlquery',
    0,
    'cirad',
    sql,
    sqlData,
    'layername',
    'geom',
    'fk_id_spatial_object',
    'true'
)


