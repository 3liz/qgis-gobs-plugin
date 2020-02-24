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
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
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

class GetSeriesData(GetDataAsLayer):
    """

    """

    GEOM_FIELD = None
    SERIE = 'SERIE'
    SERIE_ID = 'SERIE_ID'
    SERIES_DICT = {}

    def name(self):
        return 'get_series_data'

    def displayName(self):
        return self.tr('Get series data')

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

        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # List of series
        sql = '''
            SELECT s.id,
            concat(
                id_title,
                ' (', p.pr_code, ')',
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
        dbpluginclass = createDbPlugin( 'postgis' )
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        data = []
        if get_data =='yes' and connection_name in connections:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )

        self.SERIES = ['%s' % a[1] for a in data]
        self.SERIES_DICT = {a[1]: a[0] for a in data}
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SERIE,
                self.tr('Target serie'),
                options=self.SERIES,
                optional=False
            )
        )

        # Id of series, to get the serie directly
        # mainly used from other processing algs
        p = QgsProcessingParameterNumber(
            self.SERIE_ID,
            self.tr('Series ID. If given, it overrides previous choice'),
            optional=True,
            defaultValue=-1
        )
        p.setFlags(QgsProcessingParameterDefinition.FlagHidden)
        self.addParameter(p)

    def checkParameterValues(self, parameters, context):

        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)

        # Check serie id is in the list of existing series
        if serie_id and serie_id > 0:
            if not serie_id in self.SERIES_DICT.values():
                return False, self.tr('Series ID does not exists in the database')

        return super(GetSeriesData, self).checkParameterValues(parameters, context)


    def setSql(self, parameters, context, feedback):

        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')
        if get_data != 'yes':
            return

        # Get series id from first combo box
        serie = self.SERIES[parameters[self.SERIE]]
        id_serie = int(self.SERIES_DICT[serie])

        # Override series is from second number input
        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)
        if serie_id in self.SERIES_DICT.values():
            id_serie = serie_id

        # Get data from chosen series
        feedback.pushInfo(
            self.tr('GET DATA FROM CHOSEN SERIES')
        )
        sql = '''
            SELECT
                id_label,
                id_date_format,
                array_to_string(id_value_code, '|') AS id_value_code,
                array_to_string(id_value_type, '|') AS id_value_type,
                array_to_string(id_value_unit, '|') AS id_value_unit

            FROM gobs.indicator AS i
            INNER JOIN gobs.series AS s
                ON s.fk_id_indicator = i.id
            WHERE s.id = {0}
        '''.format(
            id_serie
        )
        [header, data, rowCount, ok, message] = fetchDataFromSqlQuery(
            connection_name,
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
        id_value_type = data[0][3].split('|')
        id_value_unit = data[0][4].split('|')

        # Build SQL
        get_values = [
            '(ob_value->>%s)::%s AS "%s"' % (
                idx,
                id_value_type[idx],
                s
            )
            for idx, s in enumerate(id_value_code)
        ]
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

        # Name given by the user
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]

        # Default name if nothing given
        if not output_layer_name.strip():
            # Get series id from first combo box
            serie = self.SERIES[parameters[self.SERIE]]
            id_serie = int(self.SERIES_DICT[serie])

            # Override series is from second number input
            serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)
            if serie_id in self.SERIES_DICT.values():
                id_serie = serie_id

            output_layer_name = [k for k,v in self.SERIES_DICT.items() if v == id_serie ][0]

        # Set layer name
        self.LAYER_NAME = output_layer_name

