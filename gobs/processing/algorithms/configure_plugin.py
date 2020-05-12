__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsExpressionContextUtils,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm


class ConfigurePlugin(BaseProcessingAlgorithm):

    CONNECTION_NAME = 'CONNECTION_NAME'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'configure_plugin'

    def displayName(self):
        return tr('Configure G-Obs plugin')

    def group(self):
        return tr('Configuration')

    def groupId(self):
        return 'gobs_configuration'

    def shortHelpString(self):
        short_help = tr(
            'You must run this script before any other script.'
            '\n'
            'Every parameter will be used in the other algorithms, as default values for parameters.'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        db_param = QgsProcessingParameterString(
            self.CONNECTION_NAME,
            tr('PostgreSQL connection to G-Obs database'),
            defaultValue=connection_name,
            optional=False
        )
        db_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.gui.wrappers_postgis.ConnectionWidgetWrapper'
            }
        })
        self.addParameter(db_param)

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

    def processAlgorithm(self, parameters, context, feedback):
        connection_name = parameters[self.CONNECTION_NAME]

        # Set global variable
        QgsExpressionContextUtils.setGlobalVariable('gobs_connection_name', connection_name)
        feedback.pushInfo(tr('PostgreSQL connection to G-Obs database') + ' = ' + connection_name)

        msg = tr('Configuration has been saved')
        feedback.pushInfo(msg)
        status = 1

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
