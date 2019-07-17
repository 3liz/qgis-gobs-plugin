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
    QgsVectorLayer,
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
from .get_data_as_layer import *
from processing.tools import postgis

class GetSpatialLayerVectorData(GetDataAsLayer):
    """

    """

    SPATIALLAYER = 'SPATIALLAYER'
    GEOM_FIELD = 'geom'

    def name(self):
        return 'get_spatial_layer_vector_data'

    def displayName(self):
        return self.tr('Get spatial layer vector data')

    def initAlgorithm(self, config):
        """
        """

        # use parent class to get other parameters
        super(self.__class__, self).initAlgorithm(config)

        # Add spatial layer choice
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


    def setSql(self, parameters, context, feedback):

        # Get id, label and geometry type from chosen spatial layer
        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        id_spatial_layer = spatiallayer.split('-')[-1].strip()
        feedback.pushInfo(
            self.tr('GET DATA FROM CHOSEN SPATIAL LAYER')
        )
        sql = "SELECT id, sl_label, sl_geometry_type FROM gobs.spatial_layer WHERE id = " + id_spatial_layer
        [header, data, rowCount, ok, message] = fetchDataFromSqlQuery(
            'gobs',
            sql
        )
        if ok:
            label = data[0][1]
            message = self.tr('* Data has been fetched for spatial layer')
            message+= ' %s !' % label
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(message)

        # Retrieve needed data
        id_spatial_layer = data[0][0]
        geometry_type = data[0][2]

        # Build SQL
        sql = '''
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
        self.SQL = sql.replace('\n', ' ').rstrip(';')

    def setLayerName(self, parameters, context, feedback):
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]
        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        if not output_layer_name.strip():
            output_layer_name = spatiallayer.split('-')[0].strip()
        self.LAYER_NAME = output_layer_name
