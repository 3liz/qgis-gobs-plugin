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
    QgsProcessingOutputVectorLayer,
    QgsVectorLayer,
    QgsDataSourceUri,
    QgsField,
    QgsFields,
    QgsFeature
)
from db_manager.db_plugins.plugin import BaseError
from db_manager.db_plugins.postgis.connector import PostGisDBConnector

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
    OUTPUT_LAYER = 'OUTPUT_LAYER'

    def name(self):
        return 'execute_sql_on_service'

    def displayName(self):
        return self.tr('Execute SQL on service database')

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

    def fetchDataFromSqlQuery(self, connector, sql):
        data = []
        header = []
        rowCount = 0
        error_message = None
        c = None
        ok = True
        #print "run query"
        try:
            c = connector._execute(None,str(sql))
            data = []
            header = connector._get_cursor_columns(c)
            if header == None:
                header = []
            if len(header) > 0:
                data = connector._fetchall(c)
            rowCount = c.rowcount
            if rowCount == -1:
                rowCount = len(data)

        except BaseError as e:
            ok = False
            error_message = e.msg

        finally:
            if c:
                #print "close connection"
                c.close()
                del c

        # Log errors
        if not ok:
            print(error_message)
            print(sql)

        return [header, data, rowCount, ok, error_message]

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        out = {
            self.OUTPUT_STATUS: 1,
            self.OUTPUT_STRING: 'ok'
        }

        service = parameters[self.PGSERVICE]
        sql = parameters[self.INPUT_SQL]

        uri = QgsDataSourceUri()
        uri.setConnection(service, '', '', '')
        try:
            connector = PostGisDBConnector(uri)
        except:
            msg = self.tr("""Cannot connect to database""")
            feedback.pushInfo(msg)
            status = 0
            # raise Exception(msg)
            return {
                self.OUTPUT_STATUS: status,
                self.OUTPUT_STRING: msg
            }

        vlayer = None
        [header, data, rowCount, ok, error_message] = self.fetchDataFromSqlQuery(connector, sql)
        if not ok:
            msg = error_message
            feedback.pushInfo(msg)
            status = 0
            # raise Exception(msg)
            return {
                self.OUTPUT_STATUS: status,
                self.OUTPUT_STRING: msg
            }

        # Get the querie features
        lines = []
        # Get the fields type
        fields = QgsFields()
        for ix in range(len(header)):
            fieldname = header[ix]
            fieldtype = QVariant.String
            fields.append(QgsField(fieldname, fieldtype))

        # Create vector layer
        vlayer = QgsVectorLayer("NoGeometry", "temp_layer", "memory")
        pr = vlayer.dataProvider()
        pr.addAttributes(fields)
        vlayer.updateFields()

        # Get the data
        line = None
        for d in data:
            line = []
            for ix in range(len(header)):
                fieldname = header[ix]
                val = d[ix]
                line.append(val)
            fet = QgsFeature()
            #fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(10,10)))
            fet.setAttributes(line)
            pr.addFeatures([fet])
            if line:
                lines.append(line)
        #vlayer.updateExtent()

        if not vlayer or not vlayer.isValid():
            msg = self.tr("""Invalid output layer""")
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

        if lines:
            context.temporaryLayerStore().addMapLayer(vlayer)
            context.addLayerToLoadOnCompletion(
                vlayer.id(),
                QgsProcessingContext.LayerDetails(
                    'SQL layer',
                    context.project(),
                    self.OUTPUT_LAYER
                )
            )
            out[self.OUTPUT_LAYER] = vlayer

        return out
