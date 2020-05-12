"""Tests for Processing algorithms."""

import os
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
from ..qgis_plugin_tools.tools.version import version

__copyright__ = "Copyright 2020, 3Liz"
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

    def test_load_structure_with_migration(self):
        """Test we can load the PostGIS structure with migrations."""
        VERSION = "0.2.2"
        provider = ProcessingProvider()
        QgsApplication.processingRegistry().addProvider(provider)

        feedback = LoggerProcessingFeedBack()
        params = {
            'OVERRIDE': True,
            'ADDTESTDATA': True,
        }

        os.environ["DATABASE_RUN_MIGRATION"] = VERSION
        try:
            processing_output = processing.run(
                "gobs:create_database_structure", params, feedback=feedback
            )
        except QgsProcessingException as e:
            self.assertTrue(False, e)
        del os.environ["DATABASE_RUN_MIGRATION"]

        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'gobs'"
        )
        records = self.cursor.fetchall()
        result = [r[0] for r in records]
        # Expected tables in the specific version written above at the beginning of the test.
        # DO NOT CHANGE HERE, change below at the end of the test.
        expected = [
            'glossary',
            'metadata',
            'r_graph_edge',
            'actor_category',
            'import',
            'observation',
            'graph_node',
            'r_indicator_node',
            'indicator',
            'protocol',
            'series',
            'actor',
            'spatial_layer',
            'spatial_object',
        ]

        self.assertCountEqual(expected, result, result)
        expected = "Gobs database structure has been successfully created to version \"{}\".".format(VERSION)
        self.assertEqual(expected, processing_output["OUTPUT_STRING"])

        sql = '''
            SELECT me_version
            FROM gobs.metadata
            ORDER BY me_version_date DESC
            LIMIT 1;
        '''
        self.cursor.execute(sql)
        record = self.cursor.fetchone()
        self.assertEqual(VERSION, record[0])

        feedback.pushDebugInfo("Update the database")
        params = {
            "CONNECTION_NAME_CENTRAL": "test",
            "RUNIT": True,
        }
        results = processing.run(
            "gobs:upgrade_database_structure", params, feedback=feedback
        )
        self.assertEqual(1, results["OUTPUT_STATUS"], 1)
        self.assertEqual(
            "Gobs database structure has been successfully upgraded to version \"{}\".".format(version()),
            results["OUTPUT_STRING"],
        )

        self.cursor.execute(sql)
        record = self.cursor.fetchone()
        self.assertEqual(version(), record[0])

        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'gobs'"
        )
        records = self.cursor.fetchall()
        result = [r[0] for r in records]
        expected = [
            'glossary',
            'metadata',
            'r_graph_edge',
            'actor_category',
            'import',
            'observation',
            'graph_node',
            'r_indicator_node',
            'indicator',
            'protocol',
            'series',
            'actor',
            'spatial_layer',
            'spatial_object',
        ]
        self.assertCountEqual(expected, result)

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
