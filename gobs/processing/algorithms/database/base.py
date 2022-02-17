__copyright__ = "Copyright 2022, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from gobs.processing.base_algorithm import BaseProcessingAlgorithm
from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsProcessingFeedback,
    QgsProviderConnectionException,
)

from gobs.qgis_plugin_tools.tools.i18n import tr

SCHEMA = "gobs"


class BaseDatabaseAlgorithm(BaseProcessingAlgorithm):

    def group(self):
        return tr('Structure')

    def groupId(self):
        return 'gobs_structure'

    @staticmethod
    def vacuum_all_tables(
        connection: QgsAbstractDatabaseProviderConnection,
        feedback: QgsProcessingFeedback,
    ):
        """Execute a vacuum to recompute the feature count."""
        for table in connection.tables(SCHEMA):

            if table.tableName().startswith("v_"):
                # We can't vacuum a view
                continue

            sql = f"VACUUM ANALYSE {SCHEMA}.{table.tableName()};"
            feedback.pushDebugInfo(sql)
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                feedback.reportError(str(e))
