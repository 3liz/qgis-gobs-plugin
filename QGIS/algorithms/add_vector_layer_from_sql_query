##cirad=group
##Add vector layer from SQL Query=name
##Database_type=selection postgis;spatialite
##Connection_name=string
##Query=longstring
##QueryData=longstring
##Layer_name=string vlayer
##Geometry_field_name=string geom
##Unique_id_field_name=string id
##Avoid_select_by_id=boolean True

from qgis.core import *
from db_manager.db_plugins.plugin import DBPlugin, Schema, Table, BaseError
from db_manager.db_plugins import createDbPlugin
from db_manager.dlg_db_error import DlgDbError

connectionName = unicode(Connection_name)
dbTypeMap = { 0: 'postgis', 1: 'spatialite' }
dbType = dbTypeMap[Database_type]

progress.setText('%s' % dbType)

# Get database connection via DbManager classes
connection = None
if connectionName:
    dbpluginclass = createDbPlugin( dbType, connectionName )
    if dbpluginclass:
        try:
            connection = dbpluginclass.connect()
        except BaseError as e:
            progress.setText(e.msg)
else:
    progress.setText('<b>## Please give a database connection name.</b>')

# Run the Query and create vector layer
layer = None
if connection:
    db = dbpluginclass.database()
    if db:

        # get a new layer name
        names = []
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            names.append( layer.name() )

        newLayerName = Layer_name
        i = 0
        while newLayerName in names:
            i+=1
            newLayerName = u"%s_%d" % (Layer_name, i)
        
        if Geometry_field_name == "None" :
            Geometry_field_name=None;
        # Create layer from query result
        layer = db.toSqlLayer(
            Query, 
            Geometry_field_name, 
            Unique_id_field_name, 
            newLayerName, 
            None, 
            Avoid_select_by_id
        )
        layerData = db.toSqlLayer(
            QueryData, 
            None, 
            "id", 
            newLayerName, 
            None, 
            Avoid_select_by_id
        )
        print(layer.id())
        if layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(layer)
        if layerData.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(layerData)
            
            rel = QgsRelation()
            rel.setReferencingLayer(layerData.id())
            rel.setReferencedLayer(layer.id())
            rel.addFieldPair( 'id', 'fk_id_spatial_object' )
            rel.setRelationId( newLayerName+'_ID' )
            rel.setRelationName( newLayerName+'_relation' )
            rel.isValid() # It will only be added if it is valid. If not, check the ids and field names
            QgsProject.instance().relationManager().addRelation( rel )
            
        
            
        else:
            progress.setText('<b>## The layer is invalid - Please check your query</b>')
    
    else:
        progress.setText('<b>## Database cannot be accessed</b>')
        
else:
    progress.setText('<b>## Cannot connect to the specified database connection name: "%s".</b>' % connectionName)
