"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = '3liz'
__date__ = '2019-02-15'
__copyright__ = '(C) 2019 by 3liz'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import configparser
import os

from db_manager.db_plugins import createDbPlugin
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString,
    QgsExpressionContextUtils,
)
from qgis.PyQt.QtCore import QCoreApplication


from .tools import fetchDataFromSqlQuery


class CreateDatabaseStructure(QgsProcessingAlgorithm):
    """
    Create gobs structure in Database
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    OVERRIDE = 'OVERRIDE'
    ADDTESTDATA = 'ADDTESTDATA'
    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'create_database_structure'

    def displayName(self):
        return self.tr('Create database structure')

    def group(self):
        return self.tr('Structure')

    def groupId(self):
        return 'gobs_structure'

    def shortHelpString(self):
        short_help = self.tr(
            'Install the G-Obs database structure with tables and function on the chosen database.'
            '\n'
            '\n'
            'This script will add a gobs schema with needed tables and functions'
            '\n'
            '\n'
            'Beware ! If you check the "override" checkboxes, you will loose all existing data in the existing gobs schema !'
        )
        return short_help

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        # INPUTS

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERRIDE,
                self.tr('Overwrite schema gobs and all data ? ** CAUTION ** It will remove all existing data !'),
                defaultValue=False,
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADDTESTDATA,
                self.tr('Add test data ?'),
                defaultValue=False,
                optional=False
            )
        )
        # OUTPUTS
        # Add output for status (integer) and message (string)
        self.addOutput(
            QgsProcessingOutputNumber(
                self.OUTPUT_STATUS,
                self.tr('Output status')
            )
        )
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                self.tr('Output message')
            )
        )

    def checkParameterValues(self, parameters, context):
        # Check that the connection name has been configured
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        if not connection_name:
            return False, self.tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        dbpluginclass = createDbPlugin('postgis')
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        if connection_name not in connections:
            return False, self.tr('The configured connection name does not exists in QGIS')

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
        msg = self.tr('Schema gobs does not exists. Continue...')
        for a in data:
            schema = a[0]
            if schema == 'gobs' and not override:
                ok = False
                msg = self.tr("Schema gobs already exists in database ! If you REALLY want to drop and recreate it (and loose all data), check the *Overwrite* checkbox")
        return ok, msg

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # Drop schema if needed
        override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        if override:
            feedback.pushInfo(self.tr("Trying to drop schema gobs..."))
            sql = 'DROP SCHEMA IF EXISTS gobs CASCADE;'

            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if ok:
                feedback.pushInfo(self.tr("Schema gobs has been dropped."))
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

        alg_dir = os.path.dirname(__file__)
        plugin_dir = os.path.join(alg_dir, '../../')

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
                    feedback.reportError('* ' + error_message)
                    raise Exception(error_message)
                    # status = 0
                    # return {
                    #   self.OUTPUT_STATUS: status,
                    #   self.OUTPUT_STRING: error_message
                    # }

        # Add version
        config = configparser.ConfigParser()
        config.read(str(os.path.join(plugin_dir, 'metadata.txt')))
        version = config['general']['version']
        sql = '''
            INSERT INTO gobs.metadata
            (me_version, me_version_date, me_status)
            VALUES (
                '%s', now()::timestamp(0), 1
            )
        ''' % version
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
            connection_name,
            sql
        )

        return {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: self.tr('*** GOBS STRUCTURE HAS BEEN SUCCESSFULLY CREATED ***')
        }
