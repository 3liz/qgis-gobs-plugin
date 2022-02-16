__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import QgsExpressionContextUtils

from gobs.qgis_plugin_tools.tools.i18n import tr

from .get_data_as_layer import GetDataAsLayer


class GetSeriesList(GetDataAsLayer):

    def __init__(self):
        super().__init__()
        self.GEOM_FIELD = None
        self.LAYER_NAME = tr('List of series')

    def name(self):
        return 'get_series_list'

    def displayName(self):
        return tr('Get the list of series')

    def group(self):
        return tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        pass

    def initAlgorithm(self, config):
        # use parent class to get other parameters
        super(self.__class__, self).initAlgorithm(config)

        # remove output layer name param
        self.removeParameter('OUTPUT_LAYER_NAME')

    def setSql(self, parameters, context, feedback):

        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')
        if get_data != 'yes':
            return

        # Build SQL
        sql = '''
            SELECT
                s.id,
                id_label AS indicator,
                id_paths AS indicator_paths,
                a_label AS actor_source,
                sl_label AS spatial_layer,
                pr_label AS protocol,
                count(o.id) AS nb_observation,
                min(o.ob_start_timestamp) AS min_date,
                max(Coalesce(o.ob_start_timestamp, o.ob_end_timestamp)) AS max_date

            FROM gobs.series s
            INNER JOIN gobs.observation o ON o.fk_id_series = s.id
            INNER JOIN gobs.actor a ON a.id = s.fk_id_actor
            INNER JOIN gobs.indicator i ON i.id = s.fk_id_indicator
            INNER JOIN gobs.spatial_layer sl ON sl.id = s.fk_id_spatial_layer
            INNER JOIN gobs.protocol p ON p.id = s.fk_id_protocol

            GROUP BY s.id, id_label, id_paths, a_label, sl_label, pr_label

        '''
        self.SQL = sql.replace('\n', ' ').rstrip(';')

    def setLayerName(self, parameters, context, feedback):
        pass
