__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProject,
)

from gobs.processing.algorithms.get_data_as_layer import GetDataAsLayer
from gobs.processing.algorithms.tools import (
    fetch_data_from_sql_query,
    get_postgis_connection_list,
    validateTimestamp,
)
from gobs.qgis_plugin_tools.tools.i18n import tr


class GetAggregatedData(GetDataAsLayer):

    GEOM_FIELD = None
    SERIE = 'SERIE'
    SERIE_ID = 'SERIE_ID'
    SERIES_DICT = {}
    AGGREGATE_FUNCTIONS_LIST = ('min', 'max', 'avg', 'sum', 'count', 'count_distinct', 'string_agg')
    AGGREGATE_FUNCTION_COMPATIBILITY = {
        'integer': ('min', 'max', 'avg', 'sum', 'count', 'count_distinct'),
        'real': ('min', 'max', 'avg', 'sum'),
        'text': ('count', 'string_agg', 'count_distinct'),
        'date': ('min', 'max', 'count_distinct'),
        'timestamp': ('min', 'max', 'count_distinct'),
        'boolean': (),
    }

    ADD_SPATIAL_OBJECT_DATA = 'ADD_SPATIAL_OBJECT_DATA'
    ADD_SPATIAL_OBJECT_GEOM = 'ADD_SPATIAL_OBJECT_GEOM'
    TEMPORAL_RESOLUTION = 'TEMPORAL_RESOLUTION'
    AGGREGATE_FUNCTIONS = 'AGGREGATE_FUNCTIONS'
    MIN_TIMESTAMP = 'MIN_TIMESTAMP'
    MAX_TIMESTAMP = 'MAX_TIMESTAMP'

    def name(self):
        return 'get_aggregated_data'

    def displayName(self):
        return tr('Get aggregated data')

    def group(self):
        return tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm allows to add a table or vector layer in your QGIS project '
            'containing the aggregated observation data from the chosen G-Obs series. '
            'The aggregation is made depending of the user input. '
            'Data are dynamically fetched from the database, meaning they are always up-to-date.'
            '\n'
            '* Names of the output layer: choose the name of the QGIS layer to create. '
            'If not given, the label of the series of observations, as written in the series combo box.'
            '\n'
            '* Series of observations: the G-Obs series containing the observation data.'
            '\n'
            '* Add spatial object ID and label ? If checked, the output layer will have '
            'two more columns with the spatial layer unique identifiers (ID and label).'
            '\n'
            '* Add spatial object geometry ? If checked, the output layer will be a spatial QGIS vector layer, '
            'displayed in the map, and not a geometryless table layer. The result can show duplicated geometries, '
            'for observations defined by the same geometry at different dates or times.'
            '\n'
            '* Timestamp extraction resolution: choose the desired temporal resolution of the output. '
            'Aggregates will be calculated (sum, average, etc.) by grouping the source data by this temporal resolution.'
            '\n'
            '* Choose aggregate functions to use: you can choose between the proposed functions.'
            ' The function will only be used for the compatible field types (ex: "avg" will not be used with text)'
            '\n'
            '* Minimum observation timestamp: if you enter a valid ISO timestamp in this field, '
            'only observations with a timestamp after this value will be processed.'
            '\n'
            '* Maximum observation timestamp: if you enter a valid ISO timestamp in this field, '
            'only observations with a timestamp before this value will be processed.'
        )
        return short_help

    def initAlgorithm(self, config):
        # use parent class to get other parameters
        super(self.__class__, self).initAlgorithm(config)

        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
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
        data = []
        if get_data == 'yes' and connection_name in get_postgis_connection_list():
            data, _ = fetch_data_from_sql_query(connection_name, sql)

        self.SERIES = ['%s' % a[1] for a in data]
        self.SERIES_DICT = {a[1]: a[0] for a in data}

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SERIE,
                tr('Series of observations'),
                options=self.SERIES,
                optional=False
            )
        )

        # Id of series, to get the series directly
        # mainly used from other processing algs
        p = QgsProcessingParameterNumber(
            self.SERIE_ID,
            tr('Series ID. If given, it overrides previous choice'),
            optional=True,
            defaultValue=-1
        )
        p.setFlags(QgsProcessingParameterDefinition.FlagHidden)
        self.addParameter(p)

        # Add spatial object data ?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_SPATIAL_OBJECT_DATA,
                tr('Add spatial object ID and label ?'),
                defaultValue=True,
                optional=False
            )
        )

        # Add spatial object geometry ?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_SPATIAL_OBJECT_GEOM,
                tr('Add spatial object geometry ?'),
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
                tr('Timestamp extraction resolution (aggregate values against this resolution)'),
                options=self.TEMPORAL_RESOLUTIONS,
                optional=False
            )
        )

        # Aggregate functions
        self.addParameter(
            QgsProcessingParameterEnum(
                self.AGGREGATE_FUNCTIONS,
                tr('Choose the aggregate functions to use'),
                options=self.AGGREGATE_FUNCTIONS_LIST,
                optional=False,
                allowMultiple=True,
                defaultValue=[a for a in range(len(self.AGGREGATE_FUNCTIONS_LIST))]
            )
        )

        # Min timestamp
        self.addParameter(
            QgsProcessingParameterString(
                self.MIN_TIMESTAMP,
                tr('Minimum observation timestamp, Ex: 2019-01-01 or 2019-01-06 00:00:00'),
                defaultValue='',
                optional=True
            )
        )

        # Max timestamp
        self.addParameter(
            QgsProcessingParameterString(
                self.MAX_TIMESTAMP,
                tr('Maximum observation timestamp, Ex:2019-12-31 or 2019-12-31 23:59:53'),
                defaultValue='',
                optional=True
            )
        )

    def checkParameterValues(self, parameters, context):

        # Check that the connection name has been configured
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        if connection_name not in get_postgis_connection_list():
            return False, tr('The configured connection name does not exists in QGIS')

        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)

        # Check series id is in the list of existing series
        if serie_id > 0:
            if serie_id not in self.SERIES_DICT.values():
                return False, tr('Series ID does not exists in the database')

        # Check timestamps
        min_timestamp = (self.parameterAsString(parameters, self.MIN_TIMESTAMP, context)).strip().replace('/', '-')
        max_timestamp = (self.parameterAsString(parameters, self.MAX_TIMESTAMP, context)).strip().replace('/', '-')
        if min_timestamp:
            ok, msg = validateTimestamp(min_timestamp)
            if not ok:
                return ok, tr('Minimum observation timestamp: ') + msg
        if max_timestamp:
            ok, msg = validateTimestamp(max_timestamp)
            if not ok:
                return ok, tr('Maximum observation timestamp: ') + msg

        return super(GetAggregatedData, self).checkParameterValues(parameters, context)

    def setSql(self, parameters, context, feedback):

        # Get parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
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
            tr('GET DATA FROM CHOSEN SERIES')
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
        data, error = fetch_data_from_sql_query(connection_name, sql)
        if not error:
            id_label = data[0][0]
            message = tr('* Data has been fetched for chosen series and related indicator')
            message += ' %s !' % id_label
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(error)

        # Retrieve needed data
        # id_label = data[0][0]
        # id_date_format = data[0][1]
        id_value_code = data[0][2].split('|')
        id_value_type = data[0][3].split('|')
        # id_value_unit = data[0][4].split('|')

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
            extract(epoch FROM period_start) AS id,
            '''
        if add_spatial_object_data and temporal_resolution:
            unique_id = '''
            row_number() OVER() AS id,
            '''

        sql += '''
            {unique_id}
            s.*

            FROM (
            SELECT
        '''.format(
            unique_id=unique_id
        )

        # Add spatial object data if asked
        if add_spatial_object_data:
            sql += '''
            o.fk_id_spatial_object, so_unique_id, so_unique_label,
            '''

        # Add spatial object geom
        if add_spatial_object_geom:
            sql += '''
            so.geom,
            '''

        # Add temporal resolution if asked: second, minute, hour, day, week, month, year
        if temporal_resolution:
            # (EXTRACT({temporal_resolution} FROM o.ob_start_timestamp))::integer AS temporal_resolution,
            sql += '''
            date_trunc('{temporal_resolution}', o.ob_start_timestamp) AS period_start,
            date_trunc('{temporal_resolution}', o.ob_start_timestamp) + '1 {temporal_resolution}'::interval - '1 second'::interval AS period_end,
            '''.format(
                temporal_resolution=temporal_resolution
            )

        # Add fields with chosen aggregate functions
        values_ls = []
        aggregate_functions = parameters[self.AGGREGATE_FUNCTIONS]
        for idx, fieldname in enumerate(id_value_code):
            for a, agg in enumerate(self.AGGREGATE_FUNCTIONS_LIST):
                # Avoid non user selected aggregate function
                if a not in aggregate_functions:
                    continue

                # Avoid incompatible aggregation function
                value_type = id_value_type[idx]
                if agg not in self.AGGREGATE_FUNCTION_COMPATIBILITY[value_type]:
                    continue

                # Adapt aggregation functions and parameters
                distinct = 'DISTINCT' if agg in ('count_distinct', 'string_agg') else ''
                agg_function = agg if agg != 'count_distinct' else 'count'
                agg_params = '' if agg != 'string_agg' else ", ', '"

                # Build aggregate
                values_ls.append(
                    '{agg_function}({distinct} (ob_value->>{idx})::{value_type} {agg_params}) AS "{agg}_{fieldname}"'.format(
                        agg_function=agg_function,
                        distinct=distinct,
                        idx=idx,
                        value_type=value_type,
                        agg_params=agg_params,
                        agg=agg,
                        fieldname=fieldname,
                    )
                )
        values = ", ".join(values_ls)
        sql += '''
            {values},
        '''.format(
            values=values
        )

        # Add information about observation timestamps
        sql += '''
            count(o.id) as observation_count,
            min(o.ob_start_timestamp) AS min_timestamp,
            max(Coalesce(o.ob_start_timestamp, ob_end_timestamp)) AS max_timestamp
        '''

        # FROM
        sql += '''
            FROM gobs.observation AS o
        '''

        # Add spatial_object table to join data
        if add_spatial_object_data or add_spatial_object_geom:
            sql += '''
            INNER JOIN gobs.spatial_object so
                ON so.id = o.fk_id_spatial_object
            '''

        # WHERE
        sql += '''
            WHERE true
        '''

        # Filter by series id
        sql += '''
            AND fk_id_series = {id_serie}
        '''.format(
            id_serie=id_serie
        )

        # Filter by min and/or max timestamps
        if min_timestamp:
            sql += '''
            AND Coalesce(ob_start_timestamp, ob_end_timestamp) >= '{timestamp}'::timestamp
            '''.format(
                timestamp=min_timestamp
            )

        if max_timestamp:
            sql += '''
            AND ob_start_timestamp <= '{timestamp}'::timestamp
            '''.format(
                timestamp=max_timestamp
            )

        # GROUP BY
        if add_spatial_object_data or add_spatial_object_geom or temporal_resolution:
            sql += '''
            GROUP BY 1
            '''

        if add_spatial_object_data:
            sql += '''
            , o.fk_id_spatial_object, so_unique_id, so_unique_label
            '''
        if add_spatial_object_geom:
            sql += '''
            , so.geom
            '''
        if temporal_resolution:
            # , EXTRACT({temporal_resolution} FROM o.ob_start_timestamp)
            sql += '''
            , date_trunc('{temporal_resolution}', o.ob_start_timestamp)
            , date_trunc('{temporal_resolution}', o.ob_start_timestamp) + '1 {temporal_resolution}'::interval - '1 second'::interval
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

        sql += '''
            ) AS s
        '''
        # Format SQL
        line_break = '''
'''
        spaces = 12 * ' '
        sql_log = sql.replace(spaces, '').replace(line_break + line_break, line_break)
        feedback.pushInfo('SQL = \n' + sql_log)

        self.SQL = sql_log.replace('\n', ' ').replace(line_break, ' ').rstrip(';')

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
            output_layer_name = [k for k, v in self.SERIES_DICT.items() if v == id_serie][0]

        # Set layer name
        self.LAYER_NAME = output_layer_name
