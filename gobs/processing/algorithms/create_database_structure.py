__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import os

from qgis.core import (
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProject,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.resources import plugin_path, plugin_test_data_path
from gobs.qgis_plugin_tools.tools.version import version
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from ...qgis_plugin_tools.tools.database import (
    available_migrations,
    fetch_data_from_sql_query,
)
from .tools import (
    getPostgisConnectionList,
)
SCHEMA = "gobs"


class CreateDatabaseStructure(BaseProcessingAlgorithm):
    """
    Create gobs structure in Database
    """

    CONNECTION_NAME = 'CONNECTION_NAME'
    OVERRIDE = 'OVERRIDE'
    ADD_TEST_DATA = 'ADD_TEST_DATA'

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
            '* PostgreSQL connection to G-Obs database: name of the database connection you would like to use for the installation.'
            '\n'
            '\n'
            'Beware ! If you check the "override" checkboxes, you will loose all existing data in the existing gobs schema !'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS
        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
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

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERRIDE,
                tr('Overwrite schema gobs and all data ? ** CAUTION ** It will remove all existing data !'),
                defaultValue=False,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_TEST_DATA,
                tr('Add test data ?'),
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
        # Check that the connection name has been configured
        connection_name = parameters[self.CONNECTION_NAME]
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        if connection_name not in getPostgisConnectionList():
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
        connection_name = parameters[self.CONNECTION_NAME]
        [header, data, rowCount, ok, error_message] = fetch_data_from_sql_query(
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
        connection_name = parameters[self.CONNECTION_NAME]

        # Drop schema if needed
        override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        if override:
            feedback.pushInfo(tr("Trying to drop schema {}…").format(SCHEMA))
            sql = "DROP SCHEMA IF EXISTS {} CASCADE;".format(SCHEMA)

            _, _, _, ok, error_message = fetch_data_from_sql_query(connection_name, sql)
            if ok:
                feedback.pushInfo(tr("Schema {} has been dropped.").format(SCHEMA))
            else:
                raise QgsProcessingException(error_message)

        # Create full structure
        sql_files = [
            "00_initialize_database.sql",
            "{}/10_FUNCTION.sql".format(SCHEMA),
            "{}/20_TABLE_SEQUENCE_DEFAULT.sql".format(SCHEMA),
            "{}/30_VIEW.sql".format(SCHEMA),
            "{}/40_INDEX.sql".format(SCHEMA),
            "{}/50_TRIGGER.sql".format(SCHEMA),
            "{}/60_CONSTRAINT.sql".format(SCHEMA),
            "{}/70_COMMENT.sql".format(SCHEMA),
            "{}/90_GLOSSARY.sql".format(SCHEMA),
            "99_finalize_database.sql",
        ]
        # Add test data
        add_test_data = self.parameterAsBool(parameters, self.ADD_TEST_DATA, context)
        if add_test_data:
            sql_files.append("99_test_data.sql")

        plugin_dir = plugin_path()
        plugin_version = version()
        dev_version = False
        run_migration = os.environ.get(
            "TEST_DATABASE_INSTALL_{}".format(SCHEMA.capitalize())
        )
        if plugin_version in ["master", "dev"] and not run_migration:
            feedback.reportError(
                "Be careful, running the install on a development branch!"
            )
            dev_version = True

        if run_migration:
            plugin_dir = plugin_test_data_path()
            feedback.reportError(
                "Be careful, running migrations on an empty database using {} "
                "instead of {}".format(run_migration, plugin_version)
            )
            plugin_version = run_migration

        # Loop sql files and run SQL code
        for sf in sql_files:
            feedback.pushInfo(sf)
            sql_file = os.path.join(plugin_dir, "install/sql/{}".format(sf))
            with open(sql_file, "r") as f:
                sql = f.read()
                if len(sql.strip()) == 0:
                    feedback.pushInfo("  Skipped (empty file)")
                    continue

                _, _, _, ok, error_message = fetch_data_from_sql_query(
                    connection_name, sql
                )
                if ok:
                    feedback.pushInfo("  Success !")
                else:
                    raise QgsProcessingException(error_message)

        # Add version
        if run_migration or not dev_version:
            metadata_version = plugin_version
        else:
            migrations = available_migrations(000000)
            last_migration = migrations[-1]
            metadata_version = (
                last_migration.replace("upgrade_to_", "").replace(".sql", "").strip()
            )
            feedback.reportError("Latest migration is {}".format(metadata_version))

        sql = """
            INSERT INTO {}.metadata
            (me_version, me_version_date, me_status)
            VALUES (
                '{}', now()::timestamp(0), 1
            )""".format(
            SCHEMA, metadata_version
        )

        fetch_data_from_sql_query(connection_name, sql)
        feedback.pushInfo(
            "Database version '{}'.".format(metadata_version)
        )

        return {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: tr(
                "*** THE STRUCTURE {} HAS BEEN CREATED WITH VERSION '{}'***".format(
                    SCHEMA, metadata_version
                )
            ),
        }
