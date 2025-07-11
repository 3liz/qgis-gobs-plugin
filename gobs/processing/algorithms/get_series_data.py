__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import os

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProject,
)

from gobs.processing.algorithms.get_data_as_layer import GetDataAsLayer
from gobs.processing.algorithms.tools import (
    fetch_data_from_sql_query,
    get_postgis_connection_list,
)
from gobs.qgis_plugin_tools.tools.i18n import tr


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
        if not connection_name:
            connection_name = os.environ.get("GOBS_CONNECTION_NAME")
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # List of series
        sql = '''
            SELECT s.id,
            concat(
                id_label,
                ' (', p.pr_label, ')',
                ' / Layer: "', sl_label, '"',
                ' / Project: "', pt_label, '"'
            ) AS label
            FROM gobs.series s
            INNER JOIN gobs.protocol p ON p.id = s.fk_id_protocol
            INNER JOIN gobs.project pt ON pt.id = s.fk_id_project
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
        if not connection_name:
            connection_name = os.environ.get("GOBS_CONNECTION_NAME")
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

        # Get series indicator dimensions codes and types (mandatory to build a flattened table
        sql = f'''
            SELECT
                d.di_code, d.di_type, d.di_label, d.di_unit
            FROM gobs.series AS s
            INNER JOIN gobs.indicator AS i
                ON i.id = s.fk_id_indicator
            INNER JOIN gobs.dimension AS d
                ON d.fk_id_indicator = i.id
            WHERE s.id = {id_serie}
            ORDER BY d.id
        '''
        data, error = fetch_data_from_sql_query(connection_name, sql)
        if not error:
            message = tr('* Properties has been fetched for the given series ID = ')
            message += ' %s !' % id_serie
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(error)

        # Retrieve needed data
        # Flatten the indicator dimensions
        flattened_dimensions = ', '.join([
            f'"{a[0]}" {a[1]}'
            for a in data
        ])

        # Build SQL
        sql = f'''
            SELECT
                g.*,
                v.*
            FROM
                gobs.get_series_data(
                    {id_serie},
                    {str(add_spatial_object_geom)}
                ) AS g,
                json_to_record(g.observation_values)
                    AS v ({flattened_dimensions})
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
