__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from qgis.core import QgsExpressionContextUtils, QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.resources import resources_path

from .algorithms.configure_plugin import ConfigurePlugin
from .algorithms.create_database_local_interface import (
    CreateDatabaseLocalInterface,
)
from .algorithms.create_database_structure import CreateDatabaseStructure
from .algorithms.get_aggregated_data import GetAggregatedData
from .algorithms.get_series_data import GetSeriesData
from .algorithms.get_series_list import GetSeriesList

# from .algorithms.import_observation_data import ImportObservationData
from .algorithms.get_spatial_layer_vector_data import GetSpatialLayerVectorData
from .algorithms.import_spatial_layer_data import ImportSpatialLayerData
from .algorithms.remove_series_data import RemoveSeriesData
from .algorithms.remove_spatial_layer_data import RemoveSpatialLayerData
from .algorithms.upgrade_database_structure import UpgradeDatabaseStructure


class GobsProvider(QgsProcessingProvider):

    def unload(self):
        QgsExpressionContextUtils.setGlobalVariable('gobs_get_database_data', 'no')

    def loadAlgorithms(self):

        # Add flag used by initAlgorithm method of algs
        # so that they do not get data from database to fill in their combo boxes
        QgsExpressionContextUtils.setGlobalVariable('gobs_get_database_data', 'no')

        self.addAlgorithm(ConfigurePlugin())

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

    def id(self):
        return 'gobs'

    def name(self):
        return tr('G-Obs')

    def longName(self):
        return self.name()

    def icon(self):
        return QIcon(resources_path('icons', 'icon.png'))
