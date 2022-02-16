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
    QgsProject,
)

from gobs.qgis_plugin_tools.tools.i18n import tr

from .get_data_as_layer import GetDataAsLayer
from .tools import fetchDataFromSqlQuery, get_postgis_connection_list


class GetSeriesData(GetDataAsLayer):

    GEOM_FIELD = None
    SERIE = 'SERIE'
    SERIE_ID = 'SERIE_ID'
    SERIES_DICT = {}
    ADD_SPATIAL_OBJECT_GEOM = 'ADD_SPATIAL_OBJECT_GEOM'

    def name(self):
        return 'get_series_data'

    def displayName(self):
        return tr('Get series data')

    def group(self):
        return tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm allows to add a table layer in your QGIS project containing the observation data from the chosen G-Obs series. Data are dynamically fetched from the database, meaning they are always up-to-date.'
            '\n'
            '* Name of the output layer: choose the name of the QGIS table layer to create. If not given, the label of the series will be used, by concatening the label of the indicator, protocol, source actor and spatial layer defining the chosen series.'
            '\n'
            '* Series of observations: choose the G-Obs series of observation you want to use as the data source.'
            '\n'
            '* Add spatial object geometry ? If checked, the output layer will be a spatial QGIS vector layer, displayed in the map, and not a geometryless table layer. The result can show duplicated geometries, for observations defined by the same geometry at different dates or times.'
            '\n'
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
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )

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

        # Add spatial object geometry ?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ADD_SPATIAL_OBJECT_GEOM,
                tr('Add spatial object geometry ?'),
                defaultValue=False,
                optional=False
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
        if serie_id and serie_id > 0:
            if serie_id not in self.SERIES_DICT.values():
                return False, tr('Series ID does not exists in the database')

        return super(GetSeriesData, self).checkParameterValues(parameters, context)

    def setSql(self, parameters, context, feedback):

        # Database connection parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
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

        # Other parameters
        add_spatial_object_geom = self.parameterAsBool(parameters, self.ADD_SPATIAL_OBJECT_GEOM, context)

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
            message = tr('* Data has been fetched for chosen series and related indicator')
            message += ' %s !' % id_label
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(message)

        # Retrieve needed data
        # id_label = data[0][0]
        # id_date_format = data[0][1]
        id_value_code = data[0][2].split('|')
        id_value_type = data[0][3].split('|')
        # id_value_unit = data[0][4].split('|')

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
            '''
        # Add spatial object geom
        if add_spatial_object_geom:
            sql += '''
            so.geom,
            '''
        sql+= '''
                ob_start_timestamp AS observation_start_timestamp,
                ob_end_timestamp AS observation_end_timestamp,
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
