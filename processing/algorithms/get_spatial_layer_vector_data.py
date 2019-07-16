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
    QgsProcessingContext,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsProcessingOutputVectorLayer
)
from .tools import *
import processing

class GetSpatialLayerVectorData(QgsProcessingAlgorithm):
    """

    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    CONNECTION_NAME = 'CONNECTION_NAME'
    SPATIALLAYER = 'SPATIALLAYER'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'
    OUTPUT_LAYER = 'OUTPUT_LAYER'
    OUTPUT_LAYER_NAME = 'OUTPUT_LAYER_NAME'

    SQL = ''

    def name(self):
        return 'get_spatial_layer_vector_data'

    def displayName(self):
        return self.tr('Get spatial layer vector data')

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

        # Database connection parameters
        db_param = QgsProcessingParameterString(
            self.CONNECTION_NAME, 'PostgreSQL connection',
            defaultValue='gobs',
            optional=False
        )
        db_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.gui.wrappers_postgis.ConnectionWidgetWrapper'
            }
        })
        self.addParameter(db_param)

        # List of spatial_layer
        sql = '''
            SELECT id, sl_label
            FROM gobs.spatial_layer
            ORDER BY sl_label
        '''
        service = 'gobs'
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
            service, sql
        )
        self.SPATIALLAYERS = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPATIALLAYER, self.tr('Spatial layer'),
                options=self.SPATIALLAYERS,
                optional=False
            )
        )

        # Name of the layer
        self.addParameter(
            QgsProcessingParameterString(
                self.OUTPUT_LAYER_NAME, self.tr('Name of the output layer'),
                optional=True
            )
        )

        # OUTPUTS
        # Add output for status (integer)
        self.addOutput(
            QgsProcessingOutputNumber(
                self.OUTPUT_STATUS, self.tr('Output status')
            )
        )
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING, self.tr('Output message')
            )
        )

        # Output vector layer
        self.addOutput(
            QgsProcessingOutputVectorLayer(
                self.OUTPUT_LAYER, self.tr('Output layer')
            )
        )


    def getSqlData(self, sql, parameters, context, feedback):
        msg = ''
        try:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                'gobs',
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
        except:
            status = 0
            msg = self.tr('* An unknown error occured while getting data from spatial layer')

        return status, msg, data

    def getSpatialLayerData(self, parameters, context, feedback):

        # Get chosen spatial layer id
        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        id_spatial_layer = spatiallayer.split('-')[-1].strip()
        feedback.pushInfo(
            self.tr('GET DATA FROM CHOSEN SPATIAL LAYER')
        )
        sql = "SELECT id, sl_label, sl_geometry_type FROM gobs.spatial_layer WHERE id = " + id_spatial_layer
        status, message, data = self.getSqlData(sql, parameters, context, feedback)
        if status:
            label = data[0][1]
            message = self.tr('* Data has been fetched for spatial layer')
            message+= ' %s !' % label
            feedback.pushInfo(
                message
            )

        return status, message, data

    def setSql(self, parameters, context, feedback):

        # Get data from spatial_layer table for this id
        status, message, data = self.getSpatialLayerData(parameters, context, feedback)
        id_spatial_layer = data[0][0]
        geometry_type = data[0][2]

        # Build SQL
        self.SQL = '''
            SELECT
                id,
                so_unique_id AS code,
                so_unique_label AS label,
                geom::geometry({1}, 4326) AS geom
            FROM gobs.spatial_object
            WHERE fk_id_spatial_layer = {0}
        '''.format(
            id_spatial_layer,
            geometry_type
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        connexion_name = parameters[self.CONNECTION_NAME]
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]
        feedback.pushInfo('Connection name = %s' % connexion_name)
        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        if not output_layer_name.strip():
            output_layer_name = spatiallayer.split('-')[0].strip()

        msg = ''
        status = 1

        self.setSql(parameters, context, feedback)

        # Import data via QGIS alg
        vector_layer = processing.run("qgis:postgisexecuteandloadsql", {
            'DATABASE': parameters[self.CONNECTION_NAME],
            'SQL': self.SQL,
            'ID_FIELD': 'id',
            'GEOMETRY_FIELD': 'geom'
        }, context=context, feedback=feedback)

        vlayer = vector_layer['OUTPUT']
        context.temporaryLayerStore().addMapLayer(vlayer)
        context.addLayerToLoadOnCompletion(
            vlayer.id(),
            QgsProcessingContext.LayerDetails(
                output_layer_name,
                context.project(),
                self.OUTPUT_LAYER
            )
        )

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg,
            self.OUTPUT_LAYER: vlayer.id()
        }
