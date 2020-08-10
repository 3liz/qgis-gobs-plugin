__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from gobs.qgis_plugin_tools.tools.resources import plugin_path

from .tools import (
    getPostgisConnectionList,
    getPostgisConnectionUriFromName,
)


class CreateManagerProjectFromTemplate(BaseProcessingAlgorithm):

    CONNECTION_NAME = 'CONNECTION_NAME'
    PROJECT_FILE = 'PROJECT_FILE'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'create_manager_project_from_template'

    def displayName(self):
        return tr('Create manager project from template')

    def group(self):
        return tr('Manage')

    def groupId(self):
        return 'gobs_manage'

    def shortHelpString(self):
        short_help = tr(
            'You must run this script before any other script.'
            '\n'
            'Every parameter will be used in the other algorithms, as default values for parameters.'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS

        # connection name
        db_param = QgsProcessingParameterString(
            self.CONNECTION_NAME,
            tr('PostgreSQL connection to G-Obs database'),
            defaultValue='',
            optional=False
        )
        db_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.gui.wrappers_postgis.ConnectionWidgetWrapper'
            }
        })
        self.addParameter(db_param)

        # target project file
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.PROJECT_FILE,
                tr('QGIS project manager file to create'),
                defaultValue='',
                optional=False,
                fileFilter='qgs'
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

        # Check that the connection name has been configured
        connection_name = parameters[self.CONNECTION_NAME]
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        if connection_name not in getPostgisConnectionList():
            return False, tr('The configured connection name does not exists in QGIS')

        return super(CreateManagerProjectFromTemplate, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):

        # Database connection parameters
        connection_name = parameters[self.CONNECTION_NAME]
        uri = getPostgisConnectionUriFromName(connection_name)
        connection_info = uri.connectionInfo()

        # Read in the template file
        template_file = plugin_path('qgis', 'gobs_manager.qgs')

        with open(template_file, 'r') as fin:
            filedata = fin.read()

        # Replace the database connection information
        filedata = filedata.replace(
            "service='gobs'",
            connection_info
        )

        # Replace also the QGIS project variable
        filedata = filedata.replace(
            "gobs_connection_name_value",
            connection_name
        )

        # Write the file out again
        project_file = self.parameterAsString(parameters, self.PROJECT_FILE, context)
        with open(project_file, 'w') as fout:
            fout.write(filedata)

        msg = tr('Manager project has been successfully created from database connection')
        msg+= ': {}'.format(connection_name)
        feedback.pushInfo(msg)
        status = 1

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
