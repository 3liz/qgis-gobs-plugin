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
    QgsProcessingParameterString,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsProcessingOutputVectorLayer
)
from .tools import *
from .get_data_as_layer import *
from processing.tools import postgis

class GetSeriesList(GetDataAsLayer):
    """

    """

    GEOM_FIELD = None
    LAYER_NAME = tr('List of series')

    def name(self):
        return 'get_series_list'

    def displayName(self):
        return self.tr('Get the list of series')

    def group(self):
        return self.tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        return getShortHelpString(os.path.basename(__file__))

    def initAlgorithm(self, config):
        """
        """
        # use parent class to get other parameters
        super(self.__class__, self).initAlgorithm(config)

        # remove output layer name param
        self.removeParameter('OUTPUT_LAYER_NAME')

    def setSql(self, parameters, context, feedback):

        # Build SQL
        sql = '''
            SELECT
                s.id,
                id_label AS indicator,
                id_paths AS indicator_paths,
                a_name AS actor_source,
                sl_label AS spatial_layer,
                pr_name AS protocol,
                count(o.id) AS nb_observation,
                min(o.ob_timestamp) AS min_date,
                max(o.ob_timestamp) AS max_date

            FROM gobs.series s
            INNER JOIN gobs.observation o ON o.fk_id_series = s.id
            INNER JOIN gobs.actor a ON a.id = s.fk_id_actor
            INNER JOIN gobs.indicator i ON i.id = s.fk_id_indicator
            INNER JOIN gobs.spatial_layer sl ON sl.id = s.fk_id_spatial_layer
            INNER JOIN gobs.protocol p ON p.id = s.fk_id_protocol

            GROUP BY s.id, id_label, id_paths, a_name, sl_label, pr_name

        '''
        self.SQL = sql.replace('\n', ' ').rstrip(';')

    def setLayerName(self, parameters, context, feedback):
        pass

