__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from db_manager.db_plugins import createDbPlugin
from qgis.core import (
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterDefinition,
    QgsProcessingOutputString,
    QgsProcessingOutputNumber,
    QgsExpressionContextUtils,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm
from .tools import fetchDataFromSqlQuery


class RemoveSeriesData(BaseProcessingAlgorithm):

    SERIE = 'SERIE'
    SERIE_ID = 'SERIE_ID'
    SERIES_DICT = {}

    RUN_DELETE = 'RUN_DELETE'
    DELETE_SERIES = 'DELETE_SERIES'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'remove_series_data'

    def displayName(self):
        return tr('Remove series data')

    def group(self):
        return tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        short_help = tr(
            'This algorithms allows to completely delete observation data for a specific series'
            '\n'
            '* Series of observations: the G-Obs series containing the observation data.'
            '\n'
            '* Check this box to delete: this box must be checked in order to proceed. It is mainly here as a security. Please check the chosen series before proceeding !'
            '\n'
            '* Also delete the series item: if you want to delete not only the observation data of the series, but also the series item in the table.'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS
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
        dbpluginclass = createDbPlugin('postgis')
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

        # Confirmation
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.RUN_DELETE,
                tr('Check this box to delete. No action will be done otherwise'),
                defaultValue=False,
            )
        )

        # Delete the series
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DELETE_SERIES,
                tr('Also delete the series item'),
                defaultValue=False,
            )
        )

        # OUTPUTS
        # Add output for status (integer)
        self.addOutput(
            QgsProcessingOutputNumber(
                self.OUTPUT_STATUS,
                tr('Output status')
            )
        )
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                tr('Output message')
            )
        )

    def checkParameterValues(self, parameters, context):
        # Check if runit is checked
        run_delete = self.parameterAsBool(parameters, self.RUN_DELETE, context)
        if not run_delete:
            msg = tr('You must check the box to delete the observation data !')
            ok = False
            return ok, msg

        # Check that the connection name has been configured
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        dbpluginclass = createDbPlugin('postgis')
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        if connection_name not in connections:
            return False, tr('The configured connection name does not exists in QGIS')

        # Check series id is in the list of existing series
        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)
        if serie_id and serie_id > 0:
            if serie_id not in self.SERIES_DICT.values():
                return False, tr('Series ID does not exists in the database')
        return super(RemoveSeriesData, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):

        # parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        delete_series = self.parameterAsBool(parameters, self.DELETE_SERIES, context)

        # Get series id from first combo box
        serie = self.SERIES[parameters[self.SERIE]]
        id_serie = int(self.SERIES_DICT[serie])

        # Override series is from second number input
        serie_id = self.parameterAsInt(parameters, self.SERIE_ID, context)
        if serie_id in self.SERIES_DICT.values():
            id_serie = serie_id

        sql = '''
            DELETE FROM gobs.observation
            WHERE fk_id_series = {0};
            SELECT setval(
                pg_get_serial_sequence('gobs.observation', 'id'),
                coalesce(max(id),0) + 1, false
            ) FROM gobs.observation;
            DELETE FROM gobs.import

            WHERE fk_id_series = {0};
            SELECT setval(
                pg_get_serial_sequence('gobs.import', 'id'),
                coalesce(max(id),0) + 1, false
            ) FROM gobs.import;
        '''.format(
            id_serie
        )

        if delete_series:
            sql+= '''
            DELETE FROM gobs.series
            WHERE id = {0};
            SELECT setval(
                pg_get_serial_sequence('gobs.series', 'id'),
                coalesce(max(id),0) + 1, false
            ) FROM gobs.series;
            '''.format(
                id_serie
            )

        [header, data, rowCount, ok, message] = fetchDataFromSqlQuery(
            connection_name,
            sql
        )
        if ok:
            message = tr('Data has been deleted for the chosen series')
            if delete_series:
                message+= '. '+ tr('The series has also been deleted')
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(message)

        status = 1
        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: message
        }
