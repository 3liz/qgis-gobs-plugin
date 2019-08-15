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
    QgsProcessingOutputString,
    QgsExpressionContextUtils
)
import processing
import os
from .tools import *
import time
from db_manager.db_plugins import createDbPlugin

class ImportObservationData(QgsProcessingAlgorithm):
    """
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.
    SERIE = 'SERIE'
    SOURCELAYER = 'SOURCELAYER'
    MANUALDATE = 'MANUALDATE'
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

        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # List of series
        sql = '''
            SELECT s.id,
            concat(
                ' Indicator: ', id_label,
                ' / Source: ', a_name,
                ' / Layer: ', sl_label
            ) AS label
            FROM gobs.series s
            INNER JOIN gobs.protocol p ON p.id = s.fk_id_protocol
            INNER JOIN gobs.actor a ON a.id = s.fk_id_actor
            INNER JOIN gobs.indicator i ON i.id = s.fk_id_indicator
            INNER JOIN gobs.spatial_layer sl ON sl.id = s.fk_id_spatial_layer
            ORDER BY label
        '''
        dbpluginclass = createDbPlugin( 'postgis' )
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        data = []
        if connection_name in connections:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
        self.SERIES = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SERIE,
                self.tr('Target serie'),
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
        # Date field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_TIMESTAMP,
                self.tr('Date and time field. ISO Format'),
                optional=True,
                parentLayerParameterName=self.SOURCELAYER
            )
        )
        # Manual date field
        self.addParameter(
            QgsProcessingParameterString(
                self.MANUALDATE,
                self.tr('Manual date or timestamp, (2019-01-06 or 2019-01-06 22:59:50) Use when the data refers to only one date or time'),
                optional=True
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
                self.OUTPUT_STRING,
                self.tr('Output message')
            )
        )


    def checkParameterValues(self, parameters, context):

        # Check date has been given
        ok = True
        field_timestamp = self.parameterAsString(parameters, self.FIELD_TIMESTAMP, context)
        manualdate = (self.parameterAsString(parameters, self.MANUALDATE, context)).strip().replace('/', '-')
        if not field_timestamp and not manualdate:
            ok = False
            msg = self.tr('You need to enter either a date/time field or a manual date/time')

        # check validity of given manual date
        if manualdate:
            ok, msg = validateTimestamp(manualdate)
            if not ok:
                return ok, self.tr('Manual date or timestamp: ') + msg
            ok = True

        if not ok:
            return False, msg
        return super(ImportObservationData, self).checkParameterValues(parameters, context)


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # parameters
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        serie = self.SERIES[parameters[self.SERIE]]
        sourcelayer = self.parameterAsVectorLayer(parameters, self.SOURCELAYER, context)
        field_timestamp = self.parameterAsString(parameters, self.FIELD_TIMESTAMP, context)
        manualdate = self.parameterAsString(parameters, self.MANUALDATE, context)
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
            'DATABASE': connection_name,
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
                connection_name,
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
                connection_name,
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
                msg = self.tr('* Indicator date format is')
                msg+= " '%s'" % id_date_format
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

            # Use the correct expression for casting date and/or time
            caster = 'timestamp'
            if id_date_format in ('year', 'month', 'day'):
                caster = 'date'

            if manualdate.strip():
                manualdate = manualdate.strip().replace('/', '-')
                if id_date_format == 'year':
                    manualdate = manualdate[0:4] + '-01-01'
                elif id_date_format == 'month':
                    manualdate = manualdate[0:7] + '-01'
                elif id_date_format == 'day':
                    manualdate = manualdate[0:10]
                else:
                    manualdate = manualdate.strip()
                casted_timestamp = '''
                    '{0}'::{1}
                '''.format(
                    manualdate,
                    caster
                )
            else:
                casted_timestamp = ''
                if id_date_format == 'year':
                    casted_timestamp = '''
                        concat( trim(s."{0}"::text), '-01-01')::{1}
                    '''.format(
                        field_timestamp,
                        caster
                    )
                else:
                    casted_timestamp = '''
                        date_trunc('{0}', s."{1}"::{2})
                    '''.format(
                        id_date_format,
                        field_timestamp,
                        caster
                    )
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
                %s
                FROM "%s"."%s" AS s
                JOIN gobs.spatial_object AS so ON so.so_unique_id = s."%s"::text
                ;
            ''' % (
                id_serie,
                id_import,
                jsonb_array,
                casted_timestamp,
                temp_schema,
                temp_table,
                field_spatial_object
            )
            try:
                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    connection_name,
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
                    connection_name,
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
                    connection_name,
                    'DELETE FROM gobs.import WHERE id = %s ' % id_import
                )

            msg = self.tr('OBSERVATION DATA HAS BEEN SUCCESSFULLY IMPORTED !')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
