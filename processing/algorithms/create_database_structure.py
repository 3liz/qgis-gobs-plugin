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

class CreateDatabaseStructure(QgsProcessingAlgorithm):
    """

    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    PGSERVICE = 'PGSERVICE'
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
        self.addParameter(
            QgsProcessingParameterString(
                self.PGSERVICE, 'PostgreSQL Service',
                defaultValue='gobs',
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OVERRIDE, 'Overwrite schema gobs and all data ? ** CAUTION **',
                defaultValue=False,
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADDTESTDATA, 'Add test data ?',
                defaultValue=False,
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


    def run_sql(self, sql, parameters, context, feedback):
        service = parameters[self.PGSERVICE]
        exec_result = processing.run("gobs:execute_sql_on_service", {
            'PGSERVICE': service,
            'INPUT_SQL': sql
        }, context=context, feedback=feedback)
        return exec_result


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
        override = parameters[self.OVERRIDE]
        get_sql = self.run_sql(sql, parameters, context, None)
        ok = bool(get_sql['OUTPUT_STATUS'])
        msg = get_sql['OUTPUT_STRING']
        if not ok:
            return ok, msg
        msg = self.tr('Schema gobs does not exists. Continue...')
        if 'OUTPUT_LAYER' in get_sql:
            for feature in get_sql['OUTPUT_LAYER'].getFeatures():
                schema = feature['schema_name']
                if schema == 'gobs' and not override:
                    ok = False
                    msg = self.tr("Schema gobs already exists in database ! If you REALLY want to drop and recreate it (and loose all data), check the Override checkbox")
        return ok, msg

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        service = parameters[self.PGSERVICE]

        # Drop schema if needed
        override = self.parameterAsBool(parameters, self.OVERRIDE, context)
        if override:
            feedback.pushInfo(self.tr("Trying to drop schema gobs..."))
            sql = 'DROP SCHEMA IF EXISTS gobs CASCADE;'
            get_sql = self.run_sql(sql, parameters, context, None)
            ok = bool(get_sql['OUTPUT_STATUS'])
            msg = get_sql['OUTPUT_STRING']
            if ok:
                feedback.pushInfo(self.tr("Schema gobs has been droped."))
            else:
                feedback.pushInfo(msg)
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



        for sf in sql_files:
            sql_file = os.path.join(plugin_dir, 'install/sql/%s' % sf)
            with open(sql_file, 'r') as f:
                sql = f.read()
                if len(sql.strip()) == 0:
                    feedback.pushInfo('* ' + sf + ' -> SKIPPED (EMPTY FILE)')
                    continue
                get_sql = self.run_sql(sql, parameters, context, None)
                ok = bool(get_sql['OUTPUT_STATUS'])
                msg = get_sql['OUTPUT_STRING']
                if ok:
                    feedback.pushInfo('* ' + sf + ' -> SUCCESS !')
                else:
                    feedback.pushInfo(msg)
                    status = 0
                    raise Exception(msg)
                    return {
                        self.OUTPUT_STATUS: status,
                        self.OUTPUT_STRING: msg
                    }

        return {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: self.tr('*** GOBS STRUCTURE HAS BEEN SUCCESSFULLY CREATED ***')
        }
