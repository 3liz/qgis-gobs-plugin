__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import time

import processing
from qgis.core import (
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterEnum,
    QgsProcessingOutputString,
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsWkbTypes,
    QgsProject,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from .tools import (
    fetchDataFromSqlQuery,
    getPostgisConnectionList,
)


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
        return tr('Import')

    def groupId(self):
        return 'gobs_import'

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
        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # List of spatial_layer
        sql = '''
            SELECT id, sl_label
            FROM gobs.spatial_layer
            ORDER BY sl_label
        '''
        data = []
        if get_data == 'yes' and connection_name in getPostgisConnectionList():
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

    def checkParameterValues(self, parameters, context):

        # Check that the connection name has been configured
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        if connection_name not in getPostgisConnectionList():
            return False, tr('The configured connection name does not exists in QGIS')

        return super(ImportSpatialLayerData, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        # parameters
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')

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
        st_multi_left = ''
        st_multi_right = ''
        if target_is_multi:
            st_multi_left = 'ST_Multi('
            st_multi_right = ')'

        # Get target geometry type in integer
        geometry_type_integer = 1
        if target_type.replace('multi', '') == 'linestring':
            geometry_type_integer = 2
        if target_type.replace('multi', '') == 'polygon':
            geometry_type_integer = 3

        # Copy data to spatial_object
        feedback.pushInfo(
            tr('COPY IMPORTED DATA TO spatial_object')
        )
        sql = '''
            INSERT INTO gobs.spatial_object
            (so_unique_id, so_unique_label, geom, fk_id_spatial_layer)
            SELECT "{so_unique_id}", "{so_unique_label}", {st_multi_left}ST_Transform(ST_CollectionExtract(ST_MakeValid(geom),{geometry_type_integer}), 4326){st_multi_right} AS geom, {id_spatial_layer}
            FROM "{temp_schema}"."{temp_table}"

            -- Update line if data already exists
            ON CONFLICT ON CONSTRAINT spatial_object_so_unique_id_fk_id_spatial_layer_key
            DO UPDATE
            SET (geom, so_unique_label) = (EXCLUDED.geom, EXCLUDED.so_unique_label)
            WHERE True
            ;
        '''.format(
            so_unique_id=uniqueid,
            so_unique_label=uniquelabel,
            st_multi_left=st_multi_left,
            geometry_type_integer=geometry_type_integer,
            st_multi_right=st_multi_right,
            id_spatial_layer=id_spatial_layer,
            temp_schema=temp_schema,
            temp_table=temp_table
        )
        feedback.pushInfo(sql)
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
        except Exception as e:
            status = 0
            msg = tr('* An unknown error occured while adding features to spatial_object table')
            msg+= ' ' + str(e)
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
