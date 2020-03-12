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
    AGGREGATE_FUNCTIONS_LIST = ('min', 'max', 'avg', 'sum')

    ADD_SPATIAL_OBJECT_DATA = 'ADD_SPATIAL_OBJECT_DATA'
    ADD_SPATIAL_OBJECT_GEOM = 'ADD_SPATIAL_OBJECT_GEOM'
    TEMPORAL_RESOLUTION = 'TEMPORAL_RESOLUTION'
    AGGREGATE_FUNCTIONS = 'AGGREGATE_FUNCTIONS'
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
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # List of series
        sql = '''
            SELECT s.id,
            concat(
                id_label,
                ' (', p.pr_label, ')',
                ' / Source: ', a_label,
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
        if get_data == 'yes' and connection_name in connections:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )

        self.SERIES = ['%s' % a[1] for a in data]
        self.SERIES_DICT = {a[1]: a[0] for a in data}

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SERIE,
                self.tr('SOURCE - Choose one serie'),
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

        # Add spatial object data ?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_SPATIAL_OBJECT_DATA,
                self.tr('FIELDS - Add spatial object ID and label ?'),
                defaultValue=True,
                optional=False
            )
        )

        # Add spatial object geometry ?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_SPATIAL_OBJECT_GEOM,
                self.tr('FIELDS - Add spatial object geometry ?'),
                defaultValue=False,
                optional=False
            )
        )


        # Aggregate with a temporal resolution, such as hour, day, etc. ?
        self.TEMPORAL_RESOLUTIONS = [
            'original',
            'second', 'minute', 'hour', 'day', 'week', 'month', 'year'
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.TEMPORAL_RESOLUTION,
                self.tr('FIELDS - Timestamp extraction resolution'),
                options=self.TEMPORAL_RESOLUTIONS,
                optional=False
            )
        )

        # Aggregate functions
        self.addParameter(
            QgsProcessingParameterEnum(
                self.AGGREGATE_FUNCTIONS,
                self.tr('FIELDS - Choose aggregate functions to use'),
                options=self.AGGREGATE_FUNCTIONS_LIST,
                optional=False,
                allowMultiple=True,
                defaultValue=[a for a in range(len(self.AGGREGATE_FUNCTIONS_LIST))]
            )
        )

        # Aggregate with a value
        # self.addParameter(
            # QgsProcessingParameterBoolean(
                # self.GROUP_BY_DISTINCT_VALUES,
                # self.tr('Group by the distinct values'),
                # defaultValue=False,
                # optional=False
            # )
        # )

        # Min timestamp
        self.addParameter(
            QgsProcessingParameterString(
                self.MIN_TIMESTAMP,
                self.tr('FILTER - Minimum timestamp, Ex: 2019-01-01 or 2019-01-06 00:00:00'),
                defaultValue='',
                optional=True
            )
        )

        # Max timestamp
        self.addParameter(
            QgsProcessingParameterString(
                self.MAX_TIMESTAMP,
                self.tr('FILTER - Maximum timestamp, Ex:2019-12-31 or 2019-12-31 23:59:53'),
                defaultValue='',
                optional=True
            )
        )

    def checkParameterValues(self, parameters, context):

        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)

        # Check serie id is in the list of existing series
        if serie_id > 0:
            if not serie_id in self.SERIES_DICT.values():
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
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')
        if get_data != 'yes':
            return

        add_spatial_object_data = self.parameterAsBool(parameters, self.ADD_SPATIAL_OBJECT_DATA, context)
        add_spatial_object_geom = self.parameterAsBool(parameters, self.ADD_SPATIAL_OBJECT_GEOM, context)
        temporal_resolution = None
        if parameters[self.TEMPORAL_RESOLUTION] > 0:
            temporal_resolution = self.TEMPORAL_RESOLUTIONS[parameters[self.TEMPORAL_RESOLUTION]]

        min_timestamp = (self.parameterAsString(parameters, self.MIN_TIMESTAMP, context)).strip().replace('/', '-')
        max_timestamp = (self.parameterAsString(parameters, self.MAX_TIMESTAMP, context)).strip().replace('/', '-')

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
        id_value_type = data[0][3].split('|')
        id_value_unit = data[0][4].split('|')

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
        if temporal_resolution:
            unique_id = '''
            extract(epoch FROM timestamp_val) AS id,
            '''
        if add_spatial_object_data and temporal_resolution:
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

        # Add temporal resolution if asked: second, minute, hour, day, week, month, year
        if temporal_resolution:
            # (EXTRACT({temporal_resolution} FROM o.ob_timestamp))::integer AS temporal_resolution,
            sql+= '''
            date_trunc('{temporal_resolution}', o.ob_timestamp) AS timestamp_val,
            '''.format(
                temporal_resolution=temporal_resolution
            )

        # Add fields with chosen aggregate functions
        values_ls = []
        aggregate_functions = parameters[self.AGGREGATE_FUNCTIONS]
        for idx, s in enumerate(id_value_code):
            for a, agg in enumerate(self.AGGREGATE_FUNCTIONS_LIST):
                if a not in aggregate_functions:
                    continue
                values_ls.append(
                    '{agg}( (ob_value->>{idx})::{id_value_type} ) AS "{agg}_{fieldname}"'.format(
                        agg=agg,
                        idx=idx,
                        id_value_type=id_value_type[idx],
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
        if add_spatial_object_data or add_spatial_object_geom or temporal_resolution:
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
        if temporal_resolution:
            # , EXTRACT({temporal_resolution} FROM o.ob_timestamp)
            sql+= '''
            , date_trunc('{temporal_resolution}', o.ob_timestamp)
            '''.format(
                temporal_resolution=temporal_resolution
            )

        # ORDER
        # if add_spatial_object_data or temporal_resolution:
            # sql+= '''
            # ORDER BY 1
            # '''

        # if add_spatial_object_data:
            # sql+= '''
            # , so_unique_label
            # '''
        # if temporal_resolution:
            # sql+= '''
            # , temporal_resolution
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
            id_serie = int(self.SERIES_DICT[serie])

            # Override series is from second number input
            serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)
            if serie_id in self.SERIES_DICT.values():
                id_serie = serie_id
            output_layer_name = [k for k,v in self.SERIES_DICT.items() if v == id_serie ][0]

        # Set layer name
        self.LAYER_NAME = output_layer_name

