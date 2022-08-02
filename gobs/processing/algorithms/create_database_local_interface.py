__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterProviderConnection,
)

from gobs.processing.algorithms.tools import (
    createAdministrationProjectFromTemplate,
    get_postgis_connection_list,
)
from gobs.qgis_plugin_tools.tools.algorithm_processing import (
    BaseProcessingAlgorithm,
)
from gobs.qgis_plugin_tools.tools.i18n import tr


class CreateDatabaseLocalInterface(BaseProcessingAlgorithm):

    CONNECTION_NAME = 'CONNECTION_NAME'
    PROJECT_FILE = 'PROJECT_FILE'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'create_database_local_interface'

    def displayName(self):
        return tr('Create database local interface')

    def group(self):
        return tr('Administration')

    def groupId(self):
        return 'gobs_administration'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm will create a new QGIS project file for G-Obs administration purpose.'
            '\n'
            '\n'
            'The generated QGIS project must then be opened by the administrator to create the needed metadata by using QGIS editing capabilities (actors, spatial layers information, indicators, etc.)'
            '\n'
            '\n'
            '* PostgreSQL connection to G-Obs database: name of the database connection you would like to use for the new QGIS project.'
            '\n'
            '* QGIS project file to create: choose the output file destination.'
        )
        return short_help

    def initAlgorithm(self, config):
        _ = config

        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            tr("Connection to the PostgreSQL database"),
            "postgres",
            defaultValue='',
            optional=False
        )
        param.setHelp(tr("The database where the schema GObs has been installed."))
        self.addParameter(param)

        # target project file
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.PROJECT_FILE,
                tr('QGIS project file to create'),
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
            return False, tr(
                'You must use the "Configure G-obs plugin" alg to set the database connection name'
            )

        # Check that it corresponds to an existing connection
        if connection_name not in get_postgis_connection_list():
            return False, tr('The configured connection name does not exists in QGIS')

        # Check if the target project file ends with qgs
        project_file = self.parameterAsString(parameters, self.PROJECT_FILE, context)
        if not project_file.endswith('.qgs'):
            return False, tr('The QGIS project file name must end with extension ".qgs"')

        # Check if the current project is an administration project
        # and if it is already configured for the chosen connection name
        p_connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        admin_project = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_is_admin_project')
        if admin_project == 'yes' and connection_name == p_connection_name:
            return False, tr(
                'The current QGIS project is already an administration project '
                'configured for the chosen database connection'
            )

        return super(CreateDatabaseLocalInterface, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):

        # Database connection parameters
        connection_name = parameters[self.CONNECTION_NAME]

        # Write the file out again
        project_file = self.parameterAsString(parameters, self.PROJECT_FILE, context)
        if not createAdministrationProjectFromTemplate(
            connection_name,
            project_file
        ):
            raise QgsProcessingException(f"Connection {connection_name} not found")

        msg = tr('QGIS Administration project has been successfully created from database connection')
        msg+= ': {}'.format(connection_name)
        feedback.pushInfo(msg)
        status = 1

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
