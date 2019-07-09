# -*- coding: utf-8 -*-

"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = '3liz'
__date__ = '2019-02-15'
__copyright__ = '(C) 2019 by 3liz'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterEnum,
    QgsProcessingOutputString
)
import processing
import os
from .tools import *
import time

class ImportObservationData(QgsProcessingAlgorithm):
    """
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    CONNECTION_NAME = 'CONNECTION_NAME'
    SERIE = 'SERIE'
    SOURCELAYER = 'SOURCELAYER'
    FIELD_TIMESTAMP = 'FIELD_TIMESTAMP'
    FIELD_SPATIAL_OBJECT = 'FIELD_SPATIAL_OBJECT'
    FIELD1 = 'FIELD1'
    FIELD2 = 'FIELD2'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    SERIES = []

    def name(self):
        return 'gobs_import_observation_data'

    def displayName(self):
        return self.tr('Import observation data')

    def group(self):
        return self.tr('Manage')

    def groupId(self):
        return 'gobs_manage'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return self.__class__()

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        # INPUTS

        # Database connection parameters
        db_param = QgsProcessingParameterString(
            self.CONNECTION_NAME, 'PostgreSQL connection',
            defaultValue='gobs',
            optional=False
        )
        db_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.gui.wrappers_postgis.ConnectionWidgetWrapper'
            }
        })
        self.addParameter(db_param)

        # List of series
        sql = '''
            SELECT s.id,
            concat(pr_name, ' / ', a_name, ' / ', id_label, ' / ', sl_label) AS label
            FROM gobs.series s
            INNER JOIN gobs.protocol p ON p.id = s.fk_id_protocol
            INNER JOIN gobs.actor a ON a.id = s.fk_id_actor
            INNER JOIN gobs.indicator i ON i.id = s.fk_id_indicator
            INNER JOIN gobs.spatial_layer sl ON sl.id = s.fk_id_spatial_layer
            ORDER BY label
        '''
        service = 'gobs'
        [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
            service, sql
        )
        self.SERIES = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SERIE, self.tr('Target serie'),
                options=self.SERIES,
                optional=False
            )
        )

        # Source layer
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SOURCELAYER,
                self.tr('Source data layer'),
                optional=False,
                types=[QgsProcessing.TypeVector]
            )
        )
        # First field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_TIMESTAMP,
                self.tr('Date and time field'),
                optional=False,
                parentLayerParameterName=self.SOURCELAYER
            )
        )
        # Spatial object id field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_SPATIAL_OBJECT,
                self.tr('Field containing the spatial object id'),
                optional=False,
                parentLayerParameterName=self.SOURCELAYER
            )
        )
        # First field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD1,
                self.tr('First field containing data'),
                optional=False,
                parentLayerParameterName=self.SOURCELAYER
            )
        )
        # Second field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD2,
                self.tr('Second field containing data'),
                optional=True,
                parentLayerParameterName=self.SOURCELAYER
            )
        )

        # OUTPUTS
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING, self.tr('Output message')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # parameters
        connexion_name = parameters[self.CONNECTION_NAME]
        feedback.pushInfo('Connection name = %s' % connexion_name)
        serie = self.SERIES[parameters[self.SERIE]]
        sourcelayer = self.parameterAsVectorLayer(parameters, self.SOURCELAYER, context)
        field_timestamp = self.parameterAsString(parameters, self.FIELD_TIMESTAMP, context)
        field_spatial_object = self.parameterAsString(parameters, self.FIELD_SPATIAL_OBJECT, context)
        field1 = self.parameterAsString(parameters, self.FIELD1, context)
        field2 = self.parameterAsString(parameters, self.FIELD2, context)

        msg = ''
        status = 1

        # Get chosen serie id
        id_serie = serie.split('-')[-1].strip()

        # Import data to temporary table
        feedback.pushInfo(
            self.tr('IMPORT SOURCE DATA INTO TEMPORARY TABLE')
        )
        temp_schema = 'public'
        temp_table = 'temp_' + str(time.time()).replace('.', '')
        ouvrages_conversion = processing.run("qgis:importintopostgis", {
            'INPUT': parameters[self.SOURCELAYER],
            'DATABASE': parameters[self.CONNECTION_NAME],
            'SCHEMA': temp_schema,
            'TABLENAME': temp_table,
            'PRIMARY_KEY': 'gobs_id',
            'GEOMETRY_COLUMN': None,
            'ENCODING': 'UTF-8',
            'OVERWRITE': True,
            'CREATEINDEX': False,
            'LOWERCASE_NAMES': False,
            'DROP_STRING_LENGTH': True,
            'FORCE_SINGLEPART': False
        }, context=context, feedback=feedback)
        feedback.pushInfo(
            self.tr('* Source layer has been imported into temporary table')
        )

        # Create import data
        feedback.pushInfo(
            self.tr('LOG IMPORT INTO import TABLE')
        )
        sql = '''
            INSERT INTO gobs.import
            (im_timestamp, fk_id_series, im_status)
            SELECT
            -- import date
            now()::timestamp(0),
            -- serie id
            %s,
            --pending validation
            'P'
            RETURNING id
            ;
        ''' % id_serie
        id_import = None
        try:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                'gobs',
                sql
            )
            if not ok:
                status = 0
                msg = self.tr('* The following error has been raised') + '  %s' % error_message
                feedback.pushInfo(
                    msg
                )
            else:
                status = 1
                id_import = data[0][0]
                msg = self.tr('* New import data has been created with ID')
                msg+= ' = %s !' % id_import
                feedback.pushInfo(
                    msg
                )
        except:
            status = 0
            msg = self.tr('* An unknown error occured while adding import log item')


        # GET INFORMATION of indicator
        feedback.pushInfo(
            self.tr('GET DATA OF RELATED indicator')
        )
        sql = '''
            SELECT id_date_format
            FROM gobs.indicator AS i
            WHERE id = (
                SELECT s.fk_id_indicator
                FROM gobs.series AS s
                WHERE s.id = %s
                LIMIT 1
            )
            ;
        ''' % id_serie
        id_date_format = None
        try:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                'gobs',
                sql
            )
            if not ok:
                status = 0
                msg = self.tr('* The following error has been raised') + '  %s' % error_message
                feedback.pushInfo(
                    msg
                )
            else:
                status = 1
                id_date_format = data[0][0]
                msg = self.tr('* Indicator date format is %s')
                msg+= "'%s'" % id_date_format
                feedback.pushInfo(
                    msg
                )
        except:
            status = 0
            msg = self.tr('* An unknown error occured while getting indicator date format')


        # COPY DATA TO OBSERVATION TABLE
        if status:

            feedback.pushInfo(
                self.tr('COPY IMPORTED DATA TO observation TABLE')
            )

            # Calculate value for jsonb array destination
            jsonb_array = 'json_build_array('
            jsonb_array+= 's."%s"' % field1
            if field2 and field2 != field1:
                jsonb_array+= ', s."%s"' % field2
            jsonb_array+= ')'
            sql = '''
                INSERT INTO gobs.observation
                (fk_id_series, fk_id_spatial_object, fk_id_import, ob_value, ob_timestamp)
                SELECT
                -- id of the serie
                %s,
                -- id of the spatial object
                so.id,
                -- id of the import log
                %s,
                -- jsonb array value computed
                %s,
                -- timestamp from the source
                date_trunc('%s', s."%s")
                FROM "%s"."%s" AS s
                JOIN gobs.spatial_object AS so ON so.so_unique_id = s."%s"::text
                ;
            ''' % (
                id_serie,
                id_import,
                jsonb_array,
                id_date_format,
                field_timestamp,
                temp_schema,
                temp_table,
                field_spatial_object
            )
            try:
                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    'gobs',
                    sql
                )
                if not ok:
                    status = 0
                    msg = self.tr('* The following error has been raised') + '  %s' % error_message
                    feedback.pushInfo(
                        msg + ' \n' + sql
                    )
                else:
                    status = 1
                    msg = self.tr('* Source data has been successfully imported !')
                    feedback.pushInfo(
                        msg
                    )
            except:
                status = 0
                msg = self.tr('* An unknown error occured while adding features to spatial_object table')
            finally:

                # Remove temporary table
                feedback.pushInfo(
                    self.tr('DROP TEMPORARY DATA')
                )
                sql = '''
                    DROP TABLE IF EXISTS "%s"."%s"
                ;
                ''' % (
                    temp_schema,
                    temp_table
                )
                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    'gobs',
                    sql
                )
                if ok:
                    feedback.pushInfo(
                        self.tr('* Temporary data has been deleted.')
                    )
                else:
                    feedback.pushInfo(
                        self.tr('* An error occured while droping temporary table') + ' "%s"."%s"' % (temp_schema, temp_table)
                    )

            if not status and id_import:
                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    'gobs',
                    'DELETE FROM gobs.import WHERE id = %s ' % id_import
                )

            msg = self.tr('OBSERVATION DATA HAS BEEN SUCCESSFULLY IMPORTED !')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }