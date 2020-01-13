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
    QgsProcessingParameterNumber,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsProcessingOutputVectorLayer,
    QgsExpressionContextUtils,
    QgsProcessingParameterDefinition
)
from .tools import *
from .get_data_as_layer import *
from processing.tools import postgis
from db_manager.db_plugins import createDbPlugin

class GetSpatialLayerVectorData(GetDataAsLayer):
    """

    """

    SPATIALLAYER = 'SPATIALLAYER'
    SPATIALLAYER_ID = 'SPATIALLAYER_ID'
    GEOM_FIELD = 'geom'

    def name(self):
        return 'get_spatial_layer_vector_data'

    def displayName(self):
        return self.tr('Get spatial layer vector data')

    def group(self):
        return self.tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        return getShortHelpString(self.id())

    def initAlgorithm(self, config):
        """
        """

        # use parent class to get other parameters
        super(self.__class__, self).initAlgorithm(config)

        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # Add spatial layer choice
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
        self.SPATIALLAYERS_DICT = {a[0]: a[1] for a in data}
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPATIALLAYER,
                self.tr('Spatial layer'),
                options=self.SPATIALLAYERS,
                optional=False
            )
        )

        # Id of spatial layer, to get the layer directly
        # mainly used from other processing algs
        p = QgsProcessingParameterNumber(
            self.SPATIALLAYER_ID,
            self.tr('Spatial layer ID. If given, it overrides previous choice'),
            optional=True
        )
        p.setFlags(QgsProcessingParameterDefinition.FlagHidden)
        self.addParameter(p)

    def checkParameterValues(self, parameters, context):

        spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)

        # Check serie id is in the list of existing spatial layers
        if spatial_layer_id > 0:
            if not spatial_layer_id in self.SPATIALLAYERS_DICT:
                return False, self.tr('Spatial layer ID does not exists in the database')

        return super(GetSpatialLayerVectorData, self).checkParameterValues(parameters, context)

    def setSql(self, parameters, context, feedback):

        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # Get id, label and geometry type from chosen spatial layer
        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        id_spatial_layer = int(spatiallayer.split('-')[-1].strip())

        # Override spatial layer id from second number input
        spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)
        if spatial_layer_id in self.SPATIALLAYERS_DICT:
            id_spatial_layer = spatial_layer_id

        feedback.pushInfo(
            self.tr('GET DATA FROM CHOSEN SPATIAL LAYER')
        )
        sql = "SELECT id, sl_label, sl_geometry_type FROM gobs.spatial_layer WHERE id = %s" % id_spatial_layer
        [header, data, rowCount, ok, message] = fetchDataFromSqlQuery(
            connection_name,
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

        # Name given by the user
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]

        # Default name if nothing given
        if not output_layer_name.strip():
            # Get spatial layer id from first combo box
            spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
            id_spatial_layer = int(spatiallayer.split('-')[-1].strip())

            # Override spatial layer id from second number input
            spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)
            if spatial_layer_id in self.SPATIALLAYERS_DICT:
                id_spatial_layer = spatial_layer_id

            output_layer_name = self.SPATIALLAYERS_DICT[id_spatial_layer]

        # Set layer name
        self.LAYER_NAME = output_layer_name
