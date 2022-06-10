"""Tests for Processing algorithms."""

import os
import time

import psycopg2

from qgis.core import Qgis, QgsApplication, QgsProcessingException
from qgis.testing import unittest

if Qgis.QGIS_VERSION_INT >= 30800:
    from qgis import processing
else:
    import processing

from ..plugin_tools import available_migrations
from ..processing.provider import GobsProvider as ProcessingProvider
from ..qgis_plugin_tools.tools.logger_processing import (
    LoggerProcessingFeedBack,
)

__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

SCHEMA = "gobs"
VERSION = "0.2.2"


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
        registry = QgsApplication.processingRegistry()
        provider = ProcessingProvider()
        if not registry.providerById(provider.id()):
            registry.addProvider(provider)

        feedback = LoggerProcessingFeedBack()
        params = {
            'CONNECTION_NAME': 'test',
            'OVERRIDE': True,
            'ADD_TEST_DATA': True,
        }

        os.environ["TEST_DATABASE_INSTALL_{}".format(SCHEMA.upper())] = VERSION
        alg = "{}:create_database_structure".format(provider.id())
        processing_output = processing.run(alg, params, feedback=feedback)
        del os.environ["TEST_DATABASE_INSTALL_{}".format(SCHEMA.upper())]

        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'".format(
                SCHEMA
            )
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
        self.assertCountEqual(expected, result)
        expected = "*** THE STRUCTURE gobs HAS BEEN CREATED WITH VERSION '{}'***".format(VERSION)
        self.assertEqual(expected, processing_output["OUTPUT_STRING"])

        sql = """
            SELECT me_version
            FROM {}.metadata
            WHERE me_status = 1
            ORDER BY me_version_date DESC
            LIMIT 1;
        """.format(
            SCHEMA
        )
        self.cursor.execute(sql)
        record = self.cursor.fetchone()
        self.assertEqual(VERSION, record[0])

        feedback.pushDebugInfo("Update the database")
        params = {
            "CONNECTION_NAME": "test",
            "RUN_MIGRATIONS": True
        }
        alg = "{}:upgrade_database_structure".format(provider.id())
        results = processing.run(alg, params, feedback=feedback)
        self.assertEqual(1, results["OUTPUT_STATUS"], 1)
        self.assertEqual(
            "*** THE DATABASE STRUCTURE HAS BEEN UPDATED ***",
            results["OUTPUT_STRING"],
        )

        sql = """
            SELECT me_version
            FROM {}.metadata
            WHERE me_status = 1
            ORDER BY me_version_date DESC
            LIMIT 1;
        """.format(
            SCHEMA
        )
        self.cursor.execute(sql)
        record = self.cursor.fetchone()

        migrations = available_migrations(000000)
        last_migration = migrations[-1]
        metadata_version = (
            last_migration.replace("upgrade_to_", "").replace(".sql", "").strip()
        )
        self.assertEqual(metadata_version, record[0])

        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'".format(
                SCHEMA
            )
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
            'project',
            'project_view',
            'protocol',
            'series',
            'actor',
            'spatial_layer',
            'spatial_object',
            'deleted_data_log',
            'document',
        ]
        self.assertCountEqual(expected, result)

    def test_load_structure_without_migrations(self):
        """Test we can load the PostGIS structure without migrations."""
        registry = QgsApplication.processingRegistry()
        provider = ProcessingProvider()
        if not registry.providerById(provider.id()):
            registry.addProvider(provider)

        feedback = LoggerProcessingFeedBack()
        self.cursor.execute("SELECT version();")
        record = self.cursor.fetchone()
        feedback.pushInfo("PostgreSQL version : {}".format(record[0]))

        self.cursor.execute("SELECT PostGIS_Version();")
        record = self.cursor.fetchone()
        feedback.pushInfo("PostGIS version : {}".format(record[0]))

        params = {
            'CONNECTION_NAME': 'test',
            "OVERRIDE": True,  # Must be true, for the time in the test.
            "ADD_TEST_DATA": True,
        }

        alg = "{}:create_database_structure".format(provider.id())
        processing.run(alg, params, feedback=feedback)

        self.cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'".format(
                SCHEMA
            )
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
            'project',
            'project_view',
            'protocol',
            'series',
            'actor',
            'spatial_layer',
            'spatial_object',
            'deleted_data_log',
            'document',
        ]
        self.assertCountEqual(expected, result, result)

        feedback.pushDebugInfo("Relaunch the algorithm without override")
        params = {
            'CONNECTION_NAME': 'test',
            "OVERRIDE": False,
        }

        with self.assertRaises(QgsProcessingException):
            processing.run(alg, params, feedback=feedback)

        expected = (
            "Unable to execute algorithm\nSchema {} already exists in database ! "
            "If you REALLY want to drop and recreate it (and loose all data), "
            "check the *Overwrite* checkbox"
        ).format(SCHEMA)
        self.assertEqual(expected, feedback.last)

        feedback.pushDebugInfo("Update the database")
        params = {
            "CONNECTION_NAME": "test",
            "RUN_MIGRATIONS": True
        }
        alg = "{}:upgrade_database_structure".format(provider.id())
        results = processing.run(alg, params, feedback=feedback)
        self.assertEqual(1, results["OUTPUT_STATUS"], 1)
        self.assertEqual(
            " The database version already matches the plugin version. No upgrade needed.",
            results["OUTPUT_STRING"],
        )
