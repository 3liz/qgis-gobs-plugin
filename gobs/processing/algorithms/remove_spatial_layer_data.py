__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProject,
)

from gobs.qgis_plugin_tools.tools.algorithm_processing import (
    BaseProcessingAlgorithm,
)
from gobs.qgis_plugin_tools.tools.i18n import tr

from .tools import fetchDataFromSqlQuery, get_postgis_connection_list


class RemoveSpatialLayerData(BaseProcessingAlgorithm):

    SPATIALLAYER = 'SPATIALLAYER'
    SPATIALLAYER_ID = 'SPATIALLAYER_ID'

    RUN_DELETE = 'RUN_DELETE'
    DELETE_SPATIAL_LAYER = 'DELETE_SPATIAL_LAYER'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'remove_spatial_layer_data'

    def displayName(self):
        return tr('Remove spatial layer data')

    def group(self):
        return tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        short_help = tr(
            'This algorithms allows to completely delete spatial layer data (objects) for a specific spatial layer'
            '\n'
            '* Spatial layer: choose the G-Obs spatial layer.'
            '\n'
            '* Check this box to delete: this box must be checked in order to proceed. It is mainly here as a security. Please check the chosen spatial layer before proceeding !'
            '\n'
            '* Also delete the spatial layer item: if you want to delete not only the spatial objects of the spatial layers, but also the spatial layer item in the table.'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS
        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # Add spatial layer choice
        # List of spatial_layer
        sql = '''
            SELECT id, sl_label
            FROM gobs.spatial_layer
            ORDER BY sl_label
        '''
        data = []
        if get_data == 'yes' and connection_name in get_postgis_connection_list():
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
        self.SPATIALLAYERS = ['%s - %s' % (a[1], a[0]) for a in data]
        self.SPATIALLAYERS_DICT = {a[0]: a[1] for a in data}
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPATIALLAYER,
                tr('Spatial layer'),
                options=self.SPATIALLAYERS,
                optional=False
            )
        )

        # Id of spatial layer, to get the layer directly
        # mainly used from other processing algs
        p = QgsProcessingParameterNumber(
            self.SPATIALLAYER_ID,
            tr('Spatial layer ID. If given, it overrides previous choice'),
            optional=True,
            defaultValue=-1
        )
        p.setFlags(QgsProcessingParameterDefinition.FlagHidden)
        self.addParameter(p)

        # Confirmation
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RUN_DELETE,
                tr('Check this box to delete. No action will be done otherwise'),
                defaultValue=False,
            )
        )

        # Delete the series
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DELETE_SPATIAL_LAYER,
                tr('Also delete the spatial layer item'),
                defaultValue=False,
            )
        )

        # OUTPUTS
        # Add output for status (integer)
        self.addOutput(
            QgsProcessingOutputNumber(
                self.OUTPUT_STATUS,
                tr('Output status')
            )
        )
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                tr('Output message')
            )
        )

    def checkParameterValues(self, parameters, context):
        # Check if runit is checked
        run_delete = self.parameterAsBool(parameters, self.RUN_DELETE, context)
        if not run_delete:
            msg = tr('You must check the box to delete the spatial layer data !')
            ok = False
            return ok, msg

        # Check that the connection name has been configured
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        if connection_name not in get_postgis_connection_list():
            return False, tr('The configured connection name does not exists in QGIS')

        # Check layyer id is in the list of existing spatial layers
        spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)
        if spatial_layer_id and spatial_layer_id > 0:
            if spatial_layer_id not in self.SPATIALLAYERS_DICT:
                return False, tr('Spatial layer ID does not exists in the database')

        return super(RemoveSpatialLayerData, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):

        # parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        delete_spatial_layer = self.parameterAsBool(parameters, self.DELETE_SPATIAL_LAYER, context)

        # Get id, label and geometry type from chosen spatial layer
        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        id_spatial_layer = int(spatiallayer.split('-')[-1].strip())

        # Override spatial layer id from second number input
        spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)
        if spatial_layer_id and spatial_layer_id in self.SPATIALLAYERS_DICT:
            id_spatial_layer = spatial_layer_id

        sql = '''
            DELETE FROM gobs.spatial_object
            WHERE fk_id_spatial_layer = {0};
            SELECT setval(
                pg_get_serial_sequence('gobs.spatial_object', 'id'),
                coalesce(max(id),0) + 1, false
            ) FROM gobs.spatial_object;
        '''.format(
            id_spatial_layer
        )

        if delete_spatial_layer:
            sql+= '''
            DELETE FROM gobs.spatial_layer
            WHERE id = {0};
            SELECT setval(
                pg_get_serial_sequence('gobs.spatial_layer', 'id'),
                coalesce(max(id),0) + 1, false
            ) FROM gobs.spatial_layer;
            '''.format(
                id_spatial_layer
            )

        [header, data, rowCount, ok, message] = fetchDataFromSqlQuery(
            connection_name,
            sql
        )
        if ok:
            message = tr('Spatial objects has been deleted for the chosen spatial layer')
            if delete_spatial_layer:
                message+= '. '+ tr('The spatial layer has also been deleted')
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(message)

        status = 1
        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: message
        }
