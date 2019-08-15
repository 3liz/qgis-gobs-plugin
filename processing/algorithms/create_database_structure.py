# -*- coding: utf-8 -*-

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

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingOutputNumber,
    QgsProcessingOutputString
)

import processing
import os
from .tools import *
import configparser

class CreateDatabaseStructure(QgsProcessingAlgorithm):
    """

    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    CONNECTION_NAME = 'CONNECTION_NAME'
    OVERRIDE = 'OVERRIDE'
    ADDTESTDATA = 'ADDTESTDATA'
    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'gobs_create_database_structure'

    def displayName(self):
        return self.tr('Create database structure')

    def group(self):
        return self.tr('Structure')

    def groupId(self):
        return 'gobs_structure'

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
        db_param = QgsProcessingParameterString(
            self.CONNECTION_NAME,
            self.tr('PostgreSQL connection'),
            defaultValue='gobs',
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
                self.tr('Overwrite schema gobs and all data ? ** CAUTION **'),
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

        # Check database content
        ok, msg = self.checkSchema(parameters, context)
        if not ok:
            return False, msg
        return super(self.__class__, self).checkParameterValues(parameters, context)

    def checkSchema(self, parameters, context):
        sql = '''
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'gobs';
        '''
        connection_name = parameters[self.CONNECTION_NAME]
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
                msg = self.tr("Schema gobs already exists in database ! If you REALLY want to drop and recreate it (and loose all data), check the Override checkbox")
        return ok, msg

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        connection_name = parameters[self.CONNECTION_NAME]

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
                feedback.pushInfo(self.tr("Schema gobs has been droped."))
            else:
                feedback.pushInfo(error_message)
                status = 0
                # raise Exception(msg)
                return {
                    self.OUTPUT_STATUS: status,
                    self.OUTPUT_STRING: msg
                }

        # Create full structure
        sql_files = [
            '10_create_structure.sql',
            '90_glossary.sql'
        ]
        # Add test data
        addtestdata = self.parameterAsBool(parameters, self.ADDTESTDATA, context)
        if addtestdata:
            sql_files.append('99_test_data.sql')

        msg = ''
        alg_dir = os.path.dirname(__file__)
        plugin_dir = os.path.join(alg_dir, '../../')

        # Loop sql files and run SQL code
        for sf in sql_files:
            sql_file = os.path.join(plugin_dir, 'install/sql/%s' % sf)
            with open(sql_file, 'r') as f:
                sql = f.read()
                if len(sql.strip()) == 0:
                    feedback.pushInfo('* ' + sf + ' -> SKIPPED (EMPTY FILE)')
                    continue

                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    connection_name,
                    sql
                )
                if ok:
                    feedback.pushInfo('* ' + sf + ' -> SUCCESS !')
                else:
                    feedback.pushInfo(error_message)
                    status = 0
                    raise Exception(error_message)
                    # return {
                        # self.OUTPUT_STATUS: status,
                        # self.OUTPUT_STRING: error_message
                    # }

        # Add version
        config = configparser.ConfigParser()
        config.read(os.path.join(plugin_dir, 'metadata.txt'))
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
