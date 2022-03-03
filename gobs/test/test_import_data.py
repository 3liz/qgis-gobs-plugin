"""Tests for the import of data into the database."""

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsVectorLayer,
)

if Qgis.QGIS_VERSION_INT >= 30800:
    from qgis import processing
else:
    import processing

from ..processing.provider import GobsProvider as ProcessingProvider
from ..qgis_plugin_tools.tools.logger_processing import (
    LoggerProcessingFeedBack,
)
from ..qgis_plugin_tools.tools.resources import plugin_path
from .base_test_database import DatabaseTestCase

__copyright__ = "Copyright 2022, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"


class TestImportData(DatabaseTestCase):

    def test_schema_tables(self):
        """Test the list of tables from the gobs schema"""

        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'gobs'"
        )
        records = self.cursor.fetchall()
        result = [r[0] for r in records]
        expected = [
            "actor",
            "actor_category",
            "deleted_data_log",
            "document",
            "glossary",
            "graph_node",
            "import",
            "indicator",
            "metadata",
            "observation",
            "protocol",
            "r_graph_edge",
            "r_indicator_node",
            "series",
            "spatial_layer",
            "spatial_object",
        ]
        self.assertCountEqual(expected, result)

    def test_import_spatial_layer_pluviometer(self):
        """ Test the import of spatial layer data"""
        # setup provider
        provider = ProcessingProvider()
        registry = QgsApplication.processingRegistry()
        if not registry.providerById(provider.id()):
            registry.addProvider(provider)
        feedback = LoggerProcessingFeedBack()

        # import pluviometer v1
        alg = "{}:import_spatial_layer_data".format(provider.id())
        layer_v1 = QgsVectorLayer(
            plugin_path('install', 'test_data', 'pluviometer', 'pluviometers_v1.geojson'),
            'layer',
            'ogr'
        )
        params = {
            'SPATIALLAYER': 2,  # hardcoded
            'SOURCELAYER': layer_v1,
            'UNIQUEID': 'code_pluvio',
            'UNIQUELABEL': 'lieu_dit_station',
            'DATE_VALIDITY_MIN': 'date',
            'MANUAL_DATE_VALIDITY_MIN': '',
            'DATE_VALIDITY_MAX': '',
            'MANUAL_DATE_VALIDITY_MAX': ''
        }
        processing_output = processing.run(alg, params, feedback=feedback)

        self.assertEqual(1, processing_output["OUTPUT_STATUS"])

        # test spatial_object contains desired number of features
        sql= (
            " SELECT count(*) FROM gobs.spatial_object WHERE fk_id_spatial_layer IN ("
            "     SELECT id FROM gobs.spatial_layer WHERE sl_code = 'pluviometers'"
            " )"
        )
        self.cursor.execute(sql)
        expected = 5
        self.assertEqual((expected,), self.cursor.fetchone())

        # Import pluviometers_v2
        layer_v2 = QgsVectorLayer(
            plugin_path('install', 'test_data', 'pluviometer', 'pluviometers_v2.geojson'),
            'layer',
            'ogr'
        )
        params['SOURCELAYER'] = layer_v2
        params['DATE_VALIDITY_MAX'] = 'end_date'
        processing_output = processing.run(alg, params, feedback=feedback)

        self.assertEqual(1, processing_output["OUTPUT_STATUS"])

        # test spatial_object contains desired number of features
        sql= (
            " SELECT count(*) FROM gobs.spatial_object WHERE fk_id_spatial_layer IN ("
            "     SELECT id FROM gobs.spatial_layer WHERE sl_code = 'pluviometers'"
            " )"
        )
        self.cursor.execute(sql)
        expected = 7
        self.assertEqual((expected,), self.cursor.fetchone())

        # Test validity date has changed for the old versions remaining in spatial_object
        sql= (
            " SELECT so_valid_to::text"
            " FROM gobs.spatial_object"
            " WHERE so_unique_id = '29202002' AND so_valid_from = '2019-06-01'"
        )
        self.cursor.execute(sql)
        expected = '2019-07-01'
        self.assertEqual((expected,), self.cursor.fetchone())
