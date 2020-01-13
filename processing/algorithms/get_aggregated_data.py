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
    QgsProcessingParameterBoolean,
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

class GetAggregatedData(GetDataAsLayer):
    """

    """

    GEOM_FIELD = None
    SERIE = 'SERIE'
    SERIE_ID = 'SERIE_ID'
    SERIES_DICT = {}

    ADD_SPATIAL_OBJECT_DATA = 'ADD_SPATIAL_OBJECT_DATA'
    ADD_SPATIAL_OBJECT_GEOM = 'ADD_SPATIAL_OBJECT_GEOM'
    TIMESTAMP_STEP = 'TIMESTAMP_STEP'
    GROUP_BY_DISTINCT_VALUES = 'GROUP_BY_DISTINCT_VALUES'
    MIN_TIMESTAMP = 'MIN_TIMESTAMP'
    MAX_TIMESTAMP = 'MAX_TIMESTAMP'

    def name(self):
        return 'get_aggregated_data'

    def displayName(self):
        return self.tr('Get aggregated data')

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

        # List of series
        sql = '''
            SELECT s.id,
            concat(
                'Indicator: ', id_label,
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
        if connection_name in connections:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )

        self.SERIES = ['%s - %s' % (a[1], a[0]) for a in data]
        self.SERIES_DICT = {a[0]: a[1] for a in data}
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
            optional=True
        )
        p.setFlags(QgsProcessingParameterDefinition.FlagHidden)
        self.addParameter(p)

        # Add spatial object data ?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_SPATIAL_OBJECT_DATA,
                self.tr('Add spatial object ID and label ?'),
                defaultValue=True,
                optional=False
            )
        )

        # Add spatial object geometry ?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_SPATIAL_OBJECT_GEOM,
                self.tr('Add spatial object geometry ?'),
                defaultValue=False,
                optional=False
            )
        )


        # Aggregate with a timestamp step, such as hour, day, etc. ?
        self.TIMESTAMP_STEPS = [
            'no',
            'second', 'minute', 'hour', 'day', 'week', 'month', 'year'
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.TIMESTAMP_STEP,
                self.tr('Group by timestamp step ?'),
                options=self.TIMESTAMP_STEPS,
                optional=False
            )
        )

        # Aggregate with a value
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.GROUP_BY_DISTINCT_VALUES,
                self.tr('Group by the distinct values'),
                defaultValue=False,
                optional=False
            )
        )

        # Min timestamp
        self.addParameter(
            QgsProcessingParameterString(
                self.MIN_TIMESTAMP,
                self.tr('Minimum timestamp, Ex: 2019-01-01 or 2019-01-06 00:00:00'),
                defaultValue='',
                optional=True
            )
        )

        # Max timestamp
        self.addParameter(
            QgsProcessingParameterString(
                self.MAX_TIMESTAMP,
                self.tr('Maximum timestamp, Ex:2019-12-31 or 2019-12-31 23:59:53'),
                defaultValue='',
                optional=True
            )
        )

    def checkParameterValues(self, parameters, context):

        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)

        # Check serie id is in the list of existing series
        if serie_id > 0:
            if not serie_id in self.SERIES_DICT:
                return False, self.tr('Series ID does not exists in the database')

        # Check timestamps
        min_timestamp = (self.parameterAsString(parameters, self.MIN_TIMESTAMP, context)).strip().replace('/', '-')
        max_timestamp = (self.parameterAsString(parameters, self.MAX_TIMESTAMP, context)).strip().replace('/', '-')
        if min_timestamp:
            ok, msg = validateTimestamp(min_timestamp)
            if not ok:
                return ok, self.tr('Minimum timestamp: ') + msg
        if max_timestamp:
            ok, msg = validateTimestamp(max_timestamp)
            if not ok:
                return ok, self.tr('Maximum timestamp: ') + msg

        return super(GetAggregatedData, self).checkParameterValues(parameters, context)


    def setSql(self, parameters, context, feedback):

        # Get parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        add_spatial_object_data = self.parameterAsBool(parameters, self.ADD_SPATIAL_OBJECT_DATA, context)
        add_spatial_object_geom = self.parameterAsBool(parameters, self.ADD_SPATIAL_OBJECT_GEOM, context)
        timestamp_step = None
        if parameters[self.TIMESTAMP_STEP] > 0:
            timestamp_step = self.TIMESTAMP_STEPS[parameters[self.TIMESTAMP_STEP]]

        min_timestamp = (self.parameterAsString(parameters, self.MIN_TIMESTAMP, context)).strip().replace('/', '-')
        max_timestamp = (self.parameterAsString(parameters, self.MAX_TIMESTAMP, context)).strip().replace('/', '-')

        # Get series id from first combo box
        serie = self.SERIES[parameters[self.SERIE]]
        id_serie = int(serie.split('-')[-1].strip())

        # Override series is from second number input
        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)
        if serie_id in self.SERIES_DICT:
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
                id_value_type,
                id_value_unit
            FROM gobs.indicator AS i
            INNER JOIN gobs.series AS s
                ON s.fk_id_protocol = i.id
            WHERE s.id = {id_serie}
        '''.format(
            id_serie=id_serie
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
        id_value_type = data[0][3]
        id_value_unit = data[0][4]

        # BUILD SQL

        # SELECT
        sql = '''

            SELECT
        '''
        # We need a unique id
        unique_id = '''
            1 AS id,
        '''
        if add_spatial_object_data:
            unique_id = '''
            s.fk_id_spatial_object AS id,
            '''
        if timestamp_step:
            unique_id = '''
            extract(epoch FROM timestamp_val) AS id,
            '''
        if add_spatial_object_data and timestamp_step:
            unique_id = '''
            row_number() OVER() AS id,
            '''

        sql+= '''
            {unique_id}
            s.*

            FROM (
            SELECT
        '''.format(
            unique_id=unique_id
        )

        # Add spatial object data if asked
        if add_spatial_object_data:
            sql+= '''
            o.fk_id_spatial_object, so_unique_id, so_unique_label,
            '''

        # Add spatial object geom
        if add_spatial_object_geom:
            sql+= '''
            so.geom,
            '''

        # Add timestamp step if asked: second, minute, hour, day, week, month, year
        if timestamp_step:
            # (EXTRACT({timestamp_step} FROM o.ob_timestamp))::integer AS timestamp_step,
            sql+= '''
            date_trunc('{timestamp_step}', o.ob_timestamp) AS timestamp_val,
            '''.format(
                timestamp_step=timestamp_step
            )

        # Add values with all aggregate functions
        aggregates = ('min', 'max', 'avg', 'sum')
        values_ls = []
        for idx, s in enumerate(id_value_code):
            for agg in aggregates:
                values_ls.append(
                    '{agg}( (ob_value->>{idx})::{id_value_type} ) AS "{agg}_{fieldname}"'.format(
                        agg=agg,
                        idx=idx,
                        id_value_type=id_value_type,
                        fieldname=s
                    )
                )
        values = ", ".join(values_ls)
        sql+= '''
            {values},
        '''.format(
            values=values
        )

        # Add information about observation timestamps
        sql+= '''
            count(o.id) as observation_count,
            min(o.ob_timestamp) AS min_timestamp,
            max(o.ob_timestamp) AS max_timestamp
        '''

        # FROM
        sql+= '''
            FROM gobs.observation AS o
        '''

        # Add spatial_object table to join data
        if add_spatial_object_data or add_spatial_object_geom:
            sql+= '''
            INNER JOIN gobs.spatial_object so
                ON so.id = o.fk_id_spatial_object
            '''

        # WHERE
        sql+= '''
            WHERE true
        '''

        # Filter by series id
        sql+= '''
            AND fk_id_series = {id_serie}
        '''.format(
            id_serie=id_serie
        )

        # Filter by min and/or max timestamps
        if min_timestamp:
            sql+= '''
            AND ob_timestamp >= '{timestamp}'::timestamp
            '''.format(
                timestamp=min_timestamp
            )

        if max_timestamp:
            sql+= '''
            AND ob_timestamp <= '{timestamp}'::timestamp
            '''.format(
                timestamp=max_timestamp
            )

        # GROUP BY
        if add_spatial_object_data or add_spatial_object_geom or timestamp_step:
            sql+= '''
            GROUP BY 1
            '''

        if add_spatial_object_data:
            sql+= '''
            , o.fk_id_spatial_object, so_unique_id, so_unique_label
            '''
        if add_spatial_object_geom:
            sql+= '''
            , so.geom
            '''
        if timestamp_step:
            # , EXTRACT({timestamp_step} FROM o.ob_timestamp)
            sql+= '''
            , date_trunc('{timestamp_step}', o.ob_timestamp)
            '''.format(
                timestamp_step=timestamp_step
            )

        # ORDER
        # if add_spatial_object_data or timestamp_step:
            # sql+= '''
            # ORDER BY 1
            # '''

        # if add_spatial_object_data:
            # sql+= '''
            # , so_unique_label
            # '''
        # if timestamp_step:
            # sql+= '''
            # , timestamp_step
            # '''


        sql+= '''
            ) AS s
        '''

        feedback.pushInfo(
            self.tr('SQL = \n' + self.SQL.replace('            ', '''
''') )
        )
        self.SQL = sql.replace('\n', ' ').rstrip(';')

        # Set GEOM_FIELD depending on parameter
        if add_spatial_object_geom:
            self.GEOM_FIELD = 'geom'

    def setLayerName(self, parameters, context, feedback):

        # Name given by the user
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]

        # Default name if nothing given
        if not output_layer_name.strip():
            # Get series id from first combo box
            serie = self.SERIES[parameters[self.SERIE]]
            id_serie = int(serie.split('-')[-1].strip())

            # Override series is from second number input
            serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)
            if serie_id in self.SERIES_DICT:
                id_serie = serie_id
            output_layer_name = self.SERIES_DICT[id_serie]

        # Set layer name
        self.LAYER_NAME = output_layer_name

