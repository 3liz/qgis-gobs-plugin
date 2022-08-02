__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import QgsExpressionContextUtils, QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from gobs.plugin_tools import resources_path
from gobs.processing.algorithms.configuration.configure_plugin import (
    ConfigurePlugin,
)
from gobs.processing.algorithms.create_database_local_interface import (
    CreateDatabaseLocalInterface,
)
from gobs.processing.algorithms.database.create import CreateDatabaseStructure
from gobs.processing.algorithms.database.upgrade import (
    UpgradeDatabaseStructure,
)
from gobs.processing.algorithms.get_aggregated_data import GetAggregatedData
from gobs.processing.algorithms.get_series_data import GetSeriesData
from gobs.processing.algorithms.get_series_list import GetSeriesList

# from .algorithms.import_observation_data import ImportObservationData
from gobs.processing.algorithms.get_spatial_layer_vector_data import (
    GetSpatialLayerVectorData,
)
from gobs.processing.algorithms.import_spatial_layer_data import (
    ImportSpatialLayerData,
)
from gobs.processing.algorithms.remove_series_data import RemoveSeriesData
from gobs.processing.algorithms.remove_spatial_layer_data import (
    RemoveSpatialLayerData,
)
from gobs.qgis_plugin_tools.tools.i18n import tr


class GobsProvider(QgsProcessingProvider):

    def unload(self):
        QgsExpressionContextUtils.setGlobalVariable('gobs_get_database_data', 'no')

    def loadAlgorithms(self):

        # Add flag used by initAlgorithm method of algs
        # so that they do not get data from database to fill in their combo boxes
        QgsExpressionContextUtils.setGlobalVariable('gobs_get_database_data', 'no')

        self.addAlgorithm(ConfigurePlugin())

        # Database
        self.addAlgorithm(CreateDatabaseStructure())
        self.addAlgorithm(UpgradeDatabaseStructure())

        self.addAlgorithm(CreateDatabaseLocalInterface())

        self.addAlgorithm(ImportSpatialLayerData())
        self.addAlgorithm(GetSpatialLayerVectorData())
        self.addAlgorithm(GetSeriesData())
        self.addAlgorithm(GetSeriesList())
        self.addAlgorithm(GetAggregatedData())

        self.addAlgorithm(RemoveSeriesData())
        self.addAlgorithm(RemoveSpatialLayerData())

        # Put the flag back to yes
        QgsExpressionContextUtils.setGlobalVariable('gobs_get_database_data', 'yes')

    def id(self):  # NOQA: A003
        return 'gobs'

    def name(self):
        return tr('G-Obs')

    def longName(self):
        return self.name()

    def icon(self):
        return QIcon(str(resources_path('icons', 'icon.png')))
