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

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingContext,
    QgsProcessingAlgorithm,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsDataSourceUri,
    QgsField,
    QgsFields,
    QgsFeature
)
from db_manager.db_plugins.plugin import BaseError
from db_manager.db_plugins.postgis.connector import PostGisDBConnector

from .tools import *

class ExecuteSqlOnService(QgsProcessingAlgorithm):
    """
    Execute SQL into a PostgreSQL database given a service name
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

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
        """
        Here is where the processing itself takes place.
        """
        out = {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: 'ok'
        }
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
