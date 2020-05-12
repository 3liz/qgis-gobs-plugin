"""Tests for Processing algorithms."""

# import os
import psycopg2
import time

from qgis.core import (
    QgsApplication,
    QgsProcessingException,
    Qgis,
)
from qgis.testing import unittest

if Qgis.QGIS_VERSION_INT >= 30800:
    from qgis import processing
else:
    import processing

from ..processing.provider import GobsProvider as ProcessingProvider
from ..qgis_plugin_tools.tools.logger_processing import LoggerProcessingFeedBack
# from ..qgis_plugin_tools.tools.resources import metadata_config

__copyright__ = "Copyright 2019, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"


class TestProcessing(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = psycopg2.connect(
            user="docker", password="docker", host="db", port="5432", database="gis"
        )
        self.cursor = self.connection.cursor()

    def tearDown(self) -> None:
        del self.cursor
        del self.connection
        time.sleep(1)

    def test_load_structure_without_migrations(self):
        """Test we can load the PostGIS structure without migrations."""
        provider = ProcessingProvider()
        QgsApplication.processingRegistry().addProvider(provider)

        feedback = LoggerProcessingFeedBack()
        self.cursor.execute("SELECT version();")
        record = self.cursor.fetchone()
        feedback.pushInfo("PostgreSQL version : {}".format(record[0]))

        self.cursor.execute("SELECT PostGIS_Version();")
        record = self.cursor.fetchone()
        feedback.pushInfo("PostGIS version : {}".format(record[0]))

        params = {
            'OVERRIDE': True,
            'ADDTESTDATA': True,
        }
        processing.run("gobs:create_database_structure", params, feedback=feedback)

        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'gobs'"
        )
        records = self.cursor.fetchall()
        result = [r[0] for r in records]
        expected = [
            'observation',
            'graph_node',
            'r_indicator_node',
            'glossary',
            'actor_category',
            'metadata',
            'r_graph_edge',
            'import',
            'indicator',
            'protocol',
            'series',
            'actor',
            'spatial_layer',
            'spatial_object',
        ]
        self.assertCountEqual(expected, result, result)

        feedback.pushDebugInfo("Relaunch the algorithm without override")
        params = {
            'OVERRIDE': False,
            'ADDTESTDATA': True,
        }

        with self.assertRaises(QgsProcessingException):
            processing.run("gobs:create_database_structure", params, feedback=feedback)

        self.assertTrue(feedback.last.startswith('Unable to execute algorithm'), feedback.last)

        feedback.pushDebugInfo("Update the database")
        params = {
            "RUNIT": True,
        }
        results = processing.run(
            "gobs:upgrade_database_structure", params, feedback=feedback
        )
        self.assertEqual(1, results["OUTPUT_STATUS"], 1)
        self.assertEqual(
            "The database version already matches the plugin version. No upgrade needed.",
            results["OUTPUT_STRING"],
        )
