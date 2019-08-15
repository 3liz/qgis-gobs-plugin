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
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterEnum,
    QgsProcessingOutputString,
    QgsExpressionContextUtils
)
import processing
import os
from .tools import *
import time
from db_manager.db_plugins import createDbPlugin

class ImportSpatialLayerData(QgsProcessingAlgorithm):
    """
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    SPATIALLAYER = 'SPATIALLAYER'
    SOURCELAYER = 'SOURCELAYER'
    UNIQUEID = 'UNIQUEID'
    UNIQUELABEL = 'UNIQUELABEL'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    SPATIALLAYERS = []

    def name(self):
        return 'import_spatial_layer_data'

    def displayName(self):
        return self.tr('Import spatial layer data')

    def group(self):
        return self.tr('Manage')

    def groupId(self):
        return 'gobs_manage'

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
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # List of spatial_layer
        sql = '''
            SELECT id, sl_label
            FROM gobs.spatial_layer
            ORDER BY sl_label
        '''
        dbpluginclass = createDbPlugin( 'postgis' )
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        data = []
        if connection_name in connections:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
        self.SPATIALLAYERS = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPATIALLAYER,
                self.tr('Target spatial layer'),
                options=self.SPATIALLAYERS,
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SOURCELAYER,
                self.tr('Source data layer'),
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUEID,
                self.tr('Unique identifier'),
                parentLayerParameterName=self.SOURCELAYER
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUELABEL,
                self.tr('Unique label'),
                parentLayerParameterName=self.SOURCELAYER,
                type=QgsProcessingParameterField.String
            )
        )

        # OUTPUTS
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                self.tr('Output message')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # parameters
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        sourcelayer = self.parameterAsVectorLayer(parameters, self.SOURCELAYER, context)
        uniqueid = self.parameterAsString(parameters, self.UNIQUEID, context)
        uniquelabel = self.parameterAsString(parameters, self.UNIQUELABEL, context)

        msg = ''
        status = 1

        # Get chosen spatial layer id
        id_spatial_layer = spatiallayer.split('-')[-1].strip()

        # Import data to temporary table
        feedback.pushInfo(
            self.tr('IMPORT SOURCE LAYER INTO TEMPORARY TABLE')
        )
        temp_schema = 'public'
        temp_table = 'temp_' + str(time.time()).replace('.', '')
        ouvrages_conversion = processing.run("qgis:importintopostgis", {
            'INPUT': parameters[self.SOURCELAYER],
            'DATABASE': connection_name,
            'SCHEMA': temp_schema,
            'TABLENAME': temp_table,
            'PRIMARY_KEY': 'gobs_id',
            'GEOMETRY_COLUMN': 'geom',
            'ENCODING': 'UTF-8',
            'OVERWRITE': True,
            'CREATEINDEX': False,
            'LOWERCASE_NAMES': False,
            'DROP_STRING_LENGTH': True,
            'FORCE_SINGLEPART': False
        }, context=context, feedback=feedback)
        feedback.pushInfo(
            self.tr('* Source layer has been imported into temporary table')
        )

        # Copy data to spatial_object
        feedback.pushInfo(
            self.tr('COPY IMPORTED DATA TO spatial_object')
        )
        sql = '''
            INSERT INTO gobs.spatial_object
            (so_unique_id, so_unique_label, geom, fk_id_spatial_layer)
            SELECT "%s", "%s", ST_Transform(geom, 4326) AS geom, %s
            FROM "%s"."%s"
            ;
        ''' % (
            uniqueid,
            uniquelabel,
            id_spatial_layer,
            temp_schema,
            temp_table
        )
        try:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if not ok:
                status = 0
                msg = self.tr('* The following error has been raised') + '  %s' % error_message
                feedback.pushInfo(
                    msg
                )
            else:
                status = 1
                msg = self.tr('* Source data has been successfully imported !')
                feedback.pushInfo(
                    msg
                )
        except:
            status = 0
            msg = self.tr('* An unknown error occured while adding features to spatial_object table')
        finally:

            # Remove temporary table
            feedback.pushInfo(
                self.tr('DROP TEMPORARY DATA')
            )
            sql = '''
                DROP TABLE IF EXISTS "%s"."%s"
            ;
            ''' % (
                temp_schema,
                temp_table
            )
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if ok:
                feedback.pushInfo(
                    self.tr('* Temporary data has been deleted.')
                )
            else:
                feedback.pushInfo(
                    self.tr('* An error occured while droping temporary table') + ' "%s"."%s"' % (temp_schema, temp_table)
                )


        msg = self.tr('SPATIAL LAYER HAS BEEN SUCCESSFULLY IMPORTED !')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
