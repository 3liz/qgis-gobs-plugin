__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from processing.tools import postgis
from qgis.core import (
    QgsVectorLayer,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsProcessingOutputVectorLayer,
    QgsExpressionContextUtils,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm

from .tools import (
    getPostgisConnectionList,
)


class GetDataAsLayer(BaseProcessingAlgorithm):

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'
    OUTPUT_LAYER = 'OUTPUT_LAYER'
    OUTPUT_LAYER_NAME = 'OUTPUT_LAYER_NAME'
    OUTPUT_LAYER_RESULT_NAME = 'OUTPUT_LAYER_RESULT_NAME'

    SQL = 'SELECT * FROM gobs.indicator'
    LAYER_NAME = ''
    GEOM_FIELD = None

    def name(self):
        return 'get_data_as_layer'

    def displayName(self):
        return tr('Get data as layer')

    def group(self):
        return tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        pass

    def initAlgorithm(self, config):
        # INPUTS

        # Name of the layer
        self.addParameter(
            QgsProcessingParameterString(
                self.OUTPUT_LAYER_NAME,
                tr('Name of the output layer'),
                optional=True
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

        # Output vector layer
        self.addOutput(
            QgsProcessingOutputVectorLayer(
                self.OUTPUT_LAYER,
                tr('Output layer')
            )
        )

        # Output vector layer name (set by the user or the alg)
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_LAYER_RESULT_NAME,
                tr('Output layer name')
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

        return super(GetDataAsLayer, self).checkParameterValues(parameters, context)

    def setSql(self, parameters, context, feedback):

        self.SQL = self.SQL.replace('\n', ' ').rstrip(';')

    def setLayerName(self, parameters, context, feedback):

        # Name given by the user
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]
        self.LAYER_NAME = output_layer_name

    def processAlgorithm(self, parameters, context, feedback):
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')

        msg = ''
        status = 1

        # Set SQL
        self.setSql(parameters, context, feedback)
        # Set output layer name
        self.setLayerName(parameters, context, feedback)

        # Buid QGIS uri to load layer
        id_field = 'id'
        uri = postgis.uri_from_name(connection_name)
        uri.setDataSource("", "(" + self.SQL + ")", self.GEOM_FIELD, "", id_field)
        vlayer = QgsVectorLayer(uri.uri(), "layername", "postgres")
        if not vlayer.isValid():
            feedback.reportError(
                'SQL = \n' + self.SQL
            )
            raise QgsProcessingException(tr("""This layer is invalid!
                Please check the PostGIS log for error messages."""))

        # Load layer
        context.temporaryLayerStore().addMapLayer(vlayer)
        context.addLayerToLoadOnCompletion(
            vlayer.id(),
            QgsProcessingContext.LayerDetails(
                self.LAYER_NAME,
                context.project(),
                self.OUTPUT_LAYER
            )
        )

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg,
            self.OUTPUT_LAYER: vlayer.id(),
            self.OUTPUT_LAYER_RESULT_NAME: self.LAYER_NAME
        }
