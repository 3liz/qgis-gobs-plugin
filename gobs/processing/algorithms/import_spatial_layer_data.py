__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import time

import processing
from db_manager.db_plugins import createDbPlugin
from qgis.core import (
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterEnum,
    QgsProcessingOutputString,
    QgsExpressionContextUtils,
    QgsWkbTypes
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from .tools import fetchDataFromSqlQuery

class ImportSpatialLayerData(BaseProcessingAlgorithm):

    SPATIALLAYER = 'SPATIALLAYER'
    SOURCELAYER = 'SOURCELAYER'
    UNIQUEID = 'UNIQUEID'
    UNIQUELABEL = 'UNIQUELABEL'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    SPATIALLAYERS = []

    def name(self):
        return 'import_spatial_layer_data'

    def displayName(self):
        return tr('Import spatial layer data')

    def group(self):
        return tr('Manage')

    def groupId(self):
        return 'gobs_manage'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm allows to import data from a QGIS spatial layer into the G-Obs database'
            '\n'
            '\n'
            'The G-Obs administrator must have created the needed spatial layer beforehand by addind the required items in the related database tables: gobs.actor_category, gobs.actor and gobs.spatial_layer.'
            '\n'
            '* Target spatial layer: choose one of the spatial layers available in G-Obs database'
            '\n'
            '* Source data layer: choose the QGIS vector layer containing the spatial data you want to import into the chosen spatial layer.'
            '\n'
            '* Unique identifier: choose the field containing the unique ID. It can be an integer or a text field, but must be unique.'
            '\n'
            '* Unique label: choose the text field containing the unique label of the layer feature. You could use the QGIS field calculator to create one if needed.'
            '\n'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # List of spatial_layer
        sql = '''
            SELECT id, sl_label
            FROM gobs.spatial_layer
            ORDER BY sl_label
        '''
        dbpluginclass = createDbPlugin( 'postgis' )
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        data = []
        if get_data == 'yes' and connection_name in connections:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
        self.SPATIALLAYERS = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPATIALLAYER,
                tr('Target spatial layer'),
                options=self.SPATIALLAYERS,
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SOURCELAYER,
                tr('Source data layer'),
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUEID,
                tr('Unique identifier'),
                parentLayerParameterName=self.SOURCELAYER
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUELABEL,
                tr('Unique label'),
                parentLayerParameterName=self.SOURCELAYER,
                type=QgsProcessingParameterField.String
            )
        )

        # OUTPUTS
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                tr('Output message')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # parameters
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        sourcelayer = self.parameterAsVectorLayer(parameters, self.SOURCELAYER, context)
        uniqueid = self.parameterAsString(parameters, self.UNIQUEID, context)
        uniquelabel = self.parameterAsString(parameters, self.UNIQUELABEL, context)

        msg = ''
        status = 1

        # Get chosen spatial layer id
        id_spatial_layer = spatiallayer.split('-')[-1].strip()
        feedback.pushInfo(
            tr('CHECK COMPATIBILITY BETWEEN SOURCE AND TARGET GEOMETRY TYPES')
        )
        # Get spatial layer geometry type
        sql = '''
        SELECT sl_geometry_type
        FROM gobs.spatial_layer
        WHERE id = {0}
        LIMIT 1
        '''.format(
            id_spatial_layer
        )
        target_type = None
        geometry_type = None
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
            connection_name,
            sql
        )
        if not ok:
            status = 0
            msg = tr('* The following error has been raised') + '  %s' % error_message
            feedback.reportError(
                msg
            )
            raise QgsProcessingException(msg)
        else:
            for line in data:
                target_type = line[0].lower()

        # Check multi type
        target_is_multi = target_type.startswith('multi')

        # Get vector layer geometry type
        # And compare it with the spatial_layer type
        source_type = QgsWkbTypes.geometryDisplayString(int(sourcelayer.geometryType())).lower()
        source_wtype = QgsWkbTypes.displayString(int(sourcelayer.wkbType())).lower()
        ok = True
        if not target_type.endswith(source_type):
            ok = False
            msg = tr('Source vector layer and target spatial layer do not have compatible geometry types')
            msg+= ' - SOURCE: {}, TARGET: {}'.format(
                source_type, target_type
            )
            feedback.pushInfo(msg)
            raise QgsProcessingException(msg)

        source_is_multi = source_wtype.startswith('multi')

        # Cannot import multi type into single type target spatial layer
        if source_is_multi and not target_is_multi:
            ok = False
            msg = tr('Cannot import a vector layer with multi geometries into a target spatial layer with a simple geometry type defined')
            msg+= ' - SOURCE: {}, TARGET: {}'.format(
                source_wtype, target_type
            )
            feedback.pushInfo(msg)
            raise QgsProcessingException(msg)

        # Import data to temporary table
        feedback.pushInfo(
            tr('IMPORT SOURCE LAYER INTO TEMPORARY TABLE')
        )
        temp_schema = 'public'
        temp_table = 'temp_' + str(time.time()).replace('.', '')
        processing.run("qgis:importintopostgis", {
            'INPUT': parameters[self.SOURCELAYER],
            'DATABASE': connection_name,
            'SCHEMA': temp_schema,
            'TABLENAME': temp_table,
            'PRIMARY_KEY': 'gobs_id',
            'GEOMETRY_COLUMN': 'geom',
            'ENCODING': 'UTF-8',
            'OVERWRITE': True,
            'CREATEINDEX': False,
            'LOWERCASE_NAMES': False,
            'DROP_STRING_LENGTH': True,
            'FORCE_SINGLEPART': False
        }, context=context, feedback=feedback)
        feedback.pushInfo(
            tr('* Source layer has been imported into temporary table')
        )
        # Add ST_Multi if needed
        st_multi_a = ''
        st_multi_b = ''
        if target_is_multi:
            st_multi_a = 'ST_Multi('
            st_multi_b = ')'

        # Copy data to spatial_object
        feedback.pushInfo(
            tr('COPY IMPORTED DATA TO spatial_object')
        )
        sql = '''
            INSERT INTO gobs.spatial_object
            (so_unique_id, so_unique_label, geom, fk_id_spatial_layer)
            SELECT "%s", "%s", ST_Transform(ST_Buffer(geom,0), 4326) AS geom, %s
            FROM "%s"."%s"
            ;
        ''' % (
            uniqueid,
            uniquelabel,
            st_multi_a,
            st_multi_b,
            id_spatial_layer,
            temp_schema,
            temp_table
        )
        try:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if not ok:
                status = 0
                msg = tr('* The following error has been raised') + '  %s' % error_message
                feedback.reportError(
                    msg
                )
            else:
                status = 1
                msg = tr('* Source data has been successfully imported !')
                feedback.pushInfo(
                    msg
                )
        except Exception:
            status = 0
            msg = self.tr('* An unknown error occured while adding features to spatial_object table')
        finally:

            # Remove temporary table
            feedback.pushInfo(
                tr('DROP TEMPORARY DATA')
            )
            sql = '''
                DROP TABLE IF EXISTS "%s"."%s"
            ;
            ''' % (
                temp_schema,
                temp_table
            )
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if ok:
                feedback.pushInfo(
                    tr('* Temporary data has been deleted.')
                )
            else:
                feedback.reportError(
                    tr('* An error occured while droping temporary table') + ' "%s"."%s"' % (temp_schema, temp_table)
                )


        msg = tr('SPATIAL LAYER HAS BEEN SUCCESSFULLY IMPORTED !')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
