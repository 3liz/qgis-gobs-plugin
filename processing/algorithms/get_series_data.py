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

class GetSeriesData(GetDataAsLayer):
    """

    """

    GEOM_FIELD = None
    SERIE = 'SERIE'

    def name(self):
        return 'get_series_data'

    def displayName(self):
        return self.tr('Get series data')

    def initAlgorithm(self, config):
        """
        """

        # use parent class to get other parameters
        super(self.__class__, self).initAlgorithm(config)

        # List of series
        sql = '''
            SELECT s.id,
            concat(
                ' Indicator: ', id_label,
                ' / Source: ', a_name,
                ' / Layer: ', sl_label
            ) AS label
            FROM gobs.series s
            INNER JOIN gobs.protocol p ON p.id = s.fk_id_protocol
            INNER JOIN gobs.actor a ON a.id = s.fk_id_actor
            INNER JOIN gobs.indicator i ON i.id = s.fk_id_indicator
            INNER JOIN gobs.spatial_layer sl ON sl.id = s.fk_id_spatial_layer
            ORDER BY label
        '''
        service = 'gobs'
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
            service, sql
        )
        self.SERIES = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SERIE, self.tr('Target serie'),
                options=self.SERIES,
                optional=False
            )
        )


    def setSql(self, parameters, context, feedback):

        # Get data from other tables
        serie = self.SERIES[parameters[self.SERIE]]
        id_serie = serie.split('-')[-1].strip()

        feedback.pushInfo(
            self.tr('GET DATA FROM CHOSEN SERIES')
        )
        sql = '''
            SELECT id_label, id_date_format, array_to_string(id_value_code, '|') AS id_value_code, id_value_type, id_value_unit
            FROM gobs.indicator AS i
            INNER JOIN gobs.series AS s
                ON s.fk_id_protocol = i.id
            WHERE s.id = {0}
        '''.format(
            id_serie
        )
        [header, data, rowCount, ok, message] = fetchDataFromSqlQuery(
            'gobs',
            sql
        )
        if ok:
            id_label = data[0][0]
            message = self.tr('* Data has been fetched for chosen series and related indicator')
            message+= ' %s !' % id_label
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(message)

        # Retrieve needed data
        id_label = data[0][0]
        id_date_format = data[0][1]
        id_value_code = data[0][2].split('|')
        id_value_type = data[0][3]
        id_value_unit = data[0][4]

        # Build SQL
        get_values = ['(ob_value->>%s)::%s AS "%s"' % (idx, id_value_type, s) for idx, s in enumerate(id_value_code)]
        values = ", ".join(get_values)
        sql = '''
            SELECT
                o.id,
                so_unique_id AS spatial_object_code,
                ob_timestamp AS observation_timestamp,
                {0}
            FROM gobs.observation AS o
            INNER JOIN gobs.spatial_object AS so
                ON so.id = o.fk_id_spatial_object
            WHERE fk_id_series = {1}
        '''.format(
            values,
            id_serie
        )
        self.SQL = sql.replace('\n', ' ').rstrip(';')

    def setLayerName(self, parameters, context, feedback):
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]
        serie = self.SERIES[parameters[self.SERIE]]
        if not output_layer_name.strip():
            output_layer_name = serie.split('-')[0].strip()
        self.LAYER_NAME = output_layer_name