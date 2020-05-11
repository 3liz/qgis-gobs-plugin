__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsExpressionContextUtils,
)
from qgis.PyQt.QtCore import QCoreApplication


class ConfigurePlugin(QgsProcessingAlgorithm):

    CONNECTION_NAME = 'CONNECTION_NAME'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'configure_plugin'

    def displayName(self):
        return self.tr('Configure G-Obs plugin')

    def group(self):
        return self.tr('Configuration')

    def groupId(self):
        return 'gobs_configuration'

    def shortHelpString(self):
        short_help = self.tr(
            'You must run this script before any other script.'
            '\n'
            'Every parameter will be used in the other algorithms, as default values for parameters.'
        )
        return short_help

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()

    def initAlgorithm(self, config):
        # INPUTS
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        db_param = QgsProcessingParameterString(
            self.CONNECTION_NAME,
            self.tr('PostgreSQL connection to G-Obs database'),
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
                self.tr('Output status')
            )
        )
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                self.tr('Output message')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        connection_name = parameters[self.CONNECTION_NAME]

        # Set global variable
        QgsExpressionContextUtils.setGlobalVariable('gobs_connection_name', connection_name)
        feedback.pushInfo(self.tr('PostgreSQL connection to G-Obs database') + ' = ' + connection_name)

        msg = self.tr('Configuration has been saved')
        feedback.pushInfo(msg)
        status = 1

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
