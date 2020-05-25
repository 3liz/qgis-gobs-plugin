__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import os

from db_manager.db_plugins import createDbPlugin
from qgis.core import (
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsExpressionContextUtils,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.resources import plugin_path
from gobs.qgis_plugin_tools.tools.version import version, format_version_integer
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from gobs.qgis_plugin_tools.tools.database import (
    available_migrations,
    fetch_data_from_sql_query,
)
SCHEMA = "gobs"


class UpgradeDatabaseStructure(BaseProcessingAlgorithm):

    RUN_MIGRATIONS = "RUN_MIGRATIONS"
    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'upgrade_database_structure'

    def displayName(self):
        return tr('Upgrade database structure')

    def group(self):
        return tr('Structure')

    def groupId(self):
        return 'gobs_structure'

    def shortHelpString(self):
        short_help = tr(
            'Upgrade the G-Obs tables and functions in the chosen database.'
            '\n'
            '\n'
            'If you have upgraded your QGIS G-Obs plugin, you can run this script'
            ' to upgrade your database to the new plugin version.'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RUN_MIGRATIONS,
                tr('Check this box to upgrade. No action will be done otherwise'),
                defaultValue=False,
            )
        )
        # OUTPUTS
        # Add output for status (integer) and message (string)
        self.addOutput(
            QgsProcessingOutputNumber(
                self.OUTPUT_STATUS,
                tr('Output status')
            )
        )
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                tr('Output message')
            )
        )

    def checkParameterValues(self, parameters, context):
        # Check if runit is checked
        run_migrations = self.parameterAsBool(parameters, self.RUN_MIGRATIONS, context)
        if not run_migrations:
            msg = tr('You must check the box to run the upgrade !')
            ok = False
            return ok, msg

        # Check that the connection name has been configured
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        dbpluginclass = createDbPlugin('postgis')
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        if connection_name not in connections:
            return False, tr('The configured connection name does not exists in QGIS')

        # Check database content
        ok, msg = self.checkSchema(parameters, context)
        if not ok:
            return False, msg

        return super(UpgradeDatabaseStructure, self).checkParameterValues(parameters, context)

    def checkSchema(self, parameters, context):
        sql = '''
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'gobs';
        '''
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        [header, data, rowCount, ok, error_message] = fetch_data_from_sql_query(
            connection_name,
            sql
        )
        if not ok:
            return ok, error_message
        ok = False
        msg = tr("Schema gobs does not exist in database !")
        for a in data:
            schema = a[0]
            if schema == 'gobs':
                ok = True
                msg = ''
        return ok, msg

    def processAlgorithm(self, parameters, context, feedback):

        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # Drop schema if needed
        run_migrations = self.parameterAsBool(parameters, self.RUN_MIGRATIONS, context)
        if not run_migrations:
            msg = tr("Vous devez cocher cette case pour réaliser la mise à jour !")
            raise QgsProcessingException(msg)

        # Get database version
        sql = """
            SELECT me_version
            FROM {}.metadata
            WHERE me_status = 1
            ORDER BY me_version_date DESC
            LIMIT 1;
        """.format(
            SCHEMA
        )
        _, data, _, ok, error_message = fetch_data_from_sql_query(connection_name, sql)
        if not ok:
            raise QgsProcessingException(error_message)

        db_version = None
        for a in data:
            db_version = a[0]
        if not db_version:
            error_message = tr("No installed version found in the database !")
            raise QgsProcessingException(error_message)

        feedback.pushInfo(
            tr("Database structure version") + " = {}".format(db_version)
        )

        # Get plugin version
        plugin_version = version()
        if plugin_version in ["master", "dev"]:
            migrations = available_migrations(000000)
            last_migration = migrations[-1]
            plugin_version = (
                last_migration.replace("upgrade_to_", "").replace(".sql", "").strip()
            )
            feedback.reportError(
                "Be careful, running the migrations on a development branch!"
            )
            feedback.reportError(
                "Latest available migration is {}".format(plugin_version)
            )
        else:
            feedback.pushInfo(tr("Plugin version") + " = {}".format(plugin_version))

        # Return if nothing to do
        if db_version == plugin_version:
            return {
                self.OUTPUT_STATUS: 1,
                self.OUTPUT_STRING: tr(
                    " The database version already matches the plugin version. No upgrade needed."
                ),
            }

        db_version_integer = format_version_integer(db_version)
        sql_files = available_migrations(db_version_integer)

        # Loop sql files and run SQL code
        for sf in sql_files:
            sql_file = os.path.join(plugin_path(), "install/sql/upgrade/{}".format(sf))
            with open(sql_file, "r") as f:
                sql = f.read()
                if len(sql.strip()) == 0:
                    feedback.pushInfo('* ' + sf + ' -- SKIPPED (EMPTY FILE)')
                    continue

                # Add SQL database version in adresse.metadata
                new_db_version = (
                    sf.replace("upgrade_to_", "").replace(".sql", "").strip()
                )
                feedback.pushInfo(tr("* NEW DB VERSION ") + new_db_version)
                sql += """
                    UPDATE {}.metadata
                    SET (me_version, me_version_date)
                    = ( '{}', now()::timestamp(0) );
                """.format(
                    SCHEMA, new_db_version
                )

                _, _, _, ok, error_message = fetch_data_from_sql_query(
                    connection_name, sql
                )
                if not ok:
                    raise QgsProcessingException(error_message)

                feedback.pushInfo("* " + sf + " -- OK !")

        # Everything is fine, we now update to the plugin version
        sql = """
            UPDATE {}.metadata
            SET (me_version, me_version_date)
            = ( '{}', now()::timestamp(0) );
        """.format(
            SCHEMA, plugin_version
        )

        _, _, _, ok, error_message = fetch_data_from_sql_query(connection_name, sql)
        if not ok:
            raise QgsProcessingException(error_message)

        msg = tr("*** THE DATABASE STRUCTURE HAS BEEN UPDATED ***")
        feedback.pushInfo(msg)

        return {self.OUTPUT_STATUS: 1, self.OUTPUT_STRING: msg}
