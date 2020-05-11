__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
)
from qgis.PyQt.QtCore import QCoreApplication

from .tools import fetchDataFromSqlQuery


class ExecuteSqlOnService(QgsProcessingAlgorithm):
    """
    Execute SQL into a PostgreSQL database given a service name
    """

    PGSERVICE = 'PGSERVICE'
    INPUT_SQL = 'INPUT_SQL'
    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'execute_sql_on_service'

    def displayName(self):
        return self.tr('Execute SQL on service database')

    def group(self):
        return self.tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()

    def initAlgorithm(self, config):
        # INPUTS
        self.addParameter(
            QgsProcessingParameterString(
                self.PGSERVICE, 'PostgreSQL Service',
                defaultValue='gobs',
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_SQL, 'SQL statement',
                defaultValue="SELECT 1::integer AS gid, 'test' AS test;",
                optional=False
            )
        )

        # OUTPUTS
        # Add output for status (integer) and message (string)
        self.addOutput(
            QgsProcessingOutputNumber(
                self.OUTPUT_STATUS, self.tr('Output status')
            )
        )
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING, self.tr('Output message')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # out = {
        #     self.OUTPUT_STATUS: 1,
        #     self.OUTPUT_STRING: 'ok'
        # }
        # parameters
        service = parameters[self.PGSERVICE]
        sql = parameters[self.INPUT_SQL]

        # Run SQL query
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(service, sql)
        if not ok:
            msg = error_message
            feedback.pushInfo(msg)
            status = 0
            # raise Exception(msg)
            return {
                self.OUTPUT_STATUS: status,
                self.OUTPUT_STRING: msg
            }

        out = {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: 'Query has been successfully run'
        }

        return out
