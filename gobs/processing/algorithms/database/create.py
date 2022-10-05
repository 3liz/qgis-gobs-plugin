__copyright__ = "Copyright 2022, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

import os

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterProviderConnection,
    QgsProject,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)

from gobs.plugin_tools import (
    available_migrations,
    plugin_path,
    plugin_test_data_path,
)
from gobs.processing.algorithms.database.base import BaseDatabaseAlgorithm
from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.version import version

SCHEMA = "gobs"


class CreateDatabaseStructure(BaseDatabaseAlgorithm):
    """
    Create gobs structure in Database
    """

    CONNECTION_NAME = 'CONNECTION_NAME'
    OVERRIDE = 'OVERRIDE'
    ADD_TEST_DATA = 'ADD_TEST_DATA'
    ADD_OBSERVATION_DATA = 'ADD_OBSERVATION_DATA'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'create_database_structure'

    def displayName(self):
        return tr('Create database structure')

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

        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        param = QgsProcessingParameterProviderConnection(
            self.CONNECTION_NAME,
            tr("Connection to the PostgreSQL database"),
            "postgres",
            defaultValue=connection_name,
            optional=False,
        )
        param.setHelp(tr("The database where the schema '{}' will be installed.").format(SCHEMA))
        self.addParameter(param)

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
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_OBSERVATION_DATA,
                tr('Add observation test data ?'),
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
        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )
        connection = metadata.findConnection(connection_name)
        override = self.parameterAsBoolean(parameters, self.OVERRIDE, context)

        if 'gobs' in connection.schemas() and not override:
            msg = tr("Schema gobs already exists in database ! If you REALLY want to drop and recreate it (and loose all data), check the *Overwrite* checkbox")
            return False, msg

        return super(CreateDatabaseStructure, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):

        metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
        connection_name = self.parameterAsConnectionName(
            parameters, self.CONNECTION_NAME, context
        )

        # noinspection PyTypeChecker
        connection = metadata.findConnection(connection_name)
        if not connection:
            raise QgsProcessingException(
                f"La connexion {connection_name} n'existe pas."
            )

        # Drop schema if needed
        override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        if override:
            feedback.pushInfo(tr("Trying to drop schema {}…").format(SCHEMA))
            sql = "DROP SCHEMA IF EXISTS {} CASCADE;".format(SCHEMA)
            metadata = QgsProviderRegistry.instance().providerMetadata("postgres")
            connection_name = self.parameterAsConnectionName(
                parameters, self.CONNECTION_NAME, context
            )
            try:
                connection.executeSql(sql)
            except QgsProviderConnectionException as e:
                raise QgsProcessingException(str(e))
            feedback.pushInfo("  Success !")

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

        # Add observation data
        add_observation_data = self.parameterAsBool(parameters, self.ADD_OBSERVATION_DATA, context)
        if add_observation_data:
            sql_files.append("100_observation_data.sql")

        plugin_dir = plugin_path()
        plugin_version = version()
        dev_version = False
        run_migration = os.environ.get(
            "TEST_DATABASE_INSTALL_{}".format(SCHEMA.upper())
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

                try:
                    connection.executeSql(sql)
                except QgsProviderConnectionException as e:
                    raise QgsProcessingException(str(e))

                feedback.pushInfo("  Success !")

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

        try:
            connection.executeSql(sql)
        except QgsProviderConnectionException as e:
            raise QgsProcessingException(str(e))

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
