__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import os

from db_manager.db_plugins import createDbPlugin
from qgis.core import (
    QgsProcessingParameterBoolean,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsExpressionContextUtils, QgsProcessingException,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.resources import plugin_path, plugin_test_data_path
from gobs.qgis_plugin_tools.tools.version import version
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from .tools import fetchDataFromSqlQuery


class CreateDatabaseStructure(BaseProcessingAlgorithm):
    """
    Create gobs structure in Database
    """

    OVERRIDE = 'OVERRIDE'
    ADDTESTDATA = 'ADDTESTDATA'
    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'create_database_structure'

    def displayName(self):
        return tr('Create database structure')

    def group(self):
        return tr('Structure')

    def groupId(self):
        return 'gobs_structure'

    def shortHelpString(self):
        short_help = tr(
            'Install the G-Obs database structure with tables and function on the chosen database.'
            '\n'
            '\n'
            'This script will add a gobs schema with needed tables and functions'
            '\n'
            '\n'
            'Beware ! If you check the "override" checkboxes, you will loose all existing data in the existing gobs schema !'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERRIDE,
                tr('Overwrite schema gobs and all data ? ** CAUTION ** It will remove all existing data !'),
                defaultValue=False,
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADDTESTDATA,
                tr('Add test data ?'),
                defaultValue=False,
                optional=False
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
        return super(CreateDatabaseStructure, self).checkParameterValues(parameters, context)

    def checkSchema(self, parameters, context):
        sql = '''
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'gobs';
        '''
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
            connection_name,
            sql
        )
        if not ok:
            return ok, error_message
        override = parameters[self.OVERRIDE]
        msg = tr('Schema gobs does not exists. Continue...')
        for a in data:
            schema = a[0]
            if schema == 'gobs' and not override:
                ok = False
                msg = tr("Schema gobs already exists in database ! If you REALLY want to drop and recreate it (and loose all data), check the *Overwrite* checkbox")
        return ok, msg

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # Drop schema if needed
        override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        if override:
            feedback.pushInfo(tr("Trying to drop schema gobs..."))
            sql = 'DROP SCHEMA IF EXISTS gobs CASCADE;'

            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if ok:
                feedback.pushInfo(tr("Schema gobs has been dropped."))
            else:
                feedback.reportError(error_message)
                status = 0
                # raise Exception(msg)
                return {
                    self.OUTPUT_STATUS: status,
                    self.OUTPUT_STRING: error_message
                }

        # Create full structure
        sql_files = [
            '00_initialize_database.sql',
            'gobs/10_FUNCTION.sql',
            'gobs/20_TABLE_SEQUENCE_DEFAULT.sql',
            'gobs/30_VIEW.sql',
            'gobs/40_INDEX.sql',
            'gobs/50_TRIGGER.sql',
            'gobs/60_CONSTRAINT.sql',
            'gobs/70_COMMENT.sql',
            'gobs/90_GLOSSARY.sql',
            '99_finalize_database.sql',
        ]
        # Add test data
        addtestdata = self.parameterAsBool(parameters, self.ADDTESTDATA, context)
        if addtestdata:
            sql_files.append('99_test_data.sql')

        plugin_dir = plugin_path()
        plugin_version = version()

        run_migration = os.environ.get("DATABASE_RUN_MIGRATION")
        if run_migration:
            feedback.reportError(
                "Be careful, running migrations on an empty database using {} "
                "instead of {}".format(run_migration, plugin_version)
            )
            plugin_version = run_migration
            plugin_dir = plugin_test_data_path()

        # Loop sql files and run SQL code
        for sf in sql_files:
            feedback.pushInfo(sf)
            sql_file = os.path.join(plugin_dir, 'install/sql/%s' % sf)
            with open(sql_file, 'r') as f:
                sql = f.read()
                if len(sql.strip()) == 0:
                    feedback.pushInfo('  Skipped (empty file)')
                    continue

                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    connection_name,
                    sql
                )
                if ok:
                    feedback.pushInfo('  Success !')
                else:
                    raise QgsProcessingException(error_message)

        # Add version
        sql = '''
            INSERT INTO gobs.metadata
            (me_version, me_version_date, me_status)
            VALUES (
                '%s', now()::timestamp(0), 1
            )
        ''' % plugin_version
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
            connection_name,
            sql
        )

        return {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: tr('Gobs database structure has been successfully created to version "{}".'.format(plugin_version))
        }
