__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import time

import processing
from qgis.core import (
    QgsProcessing,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingOutputString,
    QgsExpressionContextUtils,
)

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.algorithm_processing import BaseProcessingAlgorithm

from .tools import (
    fetchDataFromSqlQuery,
    validateTimestamp,
)


class ImportObservationData(BaseProcessingAlgorithm):

    SOURCELAYER = 'SOURCELAYER'
    MANUALDATE = 'MANUALDATE'
    FIELD_TIMESTAMP = 'FIELD_TIMESTAMP'
    FIELD_SPATIAL_OBJECT = 'FIELD_SPATIAL_OBJECT'
    FIELDS = 'FIELDS'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'import_observation_data'

    def displayName(self):
        return tr('Import observation data')

    def group(self):
        return tr('Manage')

    def groupId(self):
        return 'gobs_manage'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm allows to import observation data from a QGIS vector or table layer into the G-Obs database'
            '\n'
            '\n'
            'The G-Obs administrator must have created needed series beforehand by addind the required items in the related database tables: gobs.protocol, gobs.indicator, gobs.actor and gobs.spatial_layer.'
            '\n'
            'Source data layer: choose the QGIS vector or table layer containing the observation data you want to import into the chosen series.'
            '\n'
            'Each feature of this source layer is an observation, caracterized by a spatial object, a timestamp, a vector of values, and will be imported into the database table gobs.observation.'
            '\n'
            '* Date time field: choose the field containing the exact date or date & time of each observation. Leave empty if all the features share the same date/time.'
            ' This field must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
            '* Manual date or timestamp: if all the data share the same timestamp, you can enter the exact value. For example, 2020 if all the observation concern the population of the cities in the year 2020.'
            ' This field must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
            '* Field containing the spatial object id: choose the field contaning the unique identifier of the related spatial object in the spatial layer of this series.'
            '\n'
            '* Depending of the chose series, you will need to choose the fields containing the data of each dimension of the observation vector of values.'
        )
        return short_help

    def getSerieId(self):
        """
        Get the serie ID
        To be overriden by child instances
        """
        return 0

    def initAlgorithm(self, config):
        # INPUTS
        # Source layer
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SOURCELAYER,
                tr('Source data layer'),
                optional=False,
                types=[QgsProcessing.TypeVector]
            )
        )
        # Date field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_TIMESTAMP,
                tr('Date and time field. ISO Format'),
                optional=True,
                parentLayerParameterName=self.SOURCELAYER
            )
        )
        # Manual date field
        self.addParameter(
            QgsProcessingParameterString(
                self.MANUALDATE,
                tr('Manual date or timestamp, (2019-01-06 or 2019-01-06 22:59:50) Use when the data refers to only one date or time'),
                optional=True
            )
        )
        # Spatial object id field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_SPATIAL_OBJECT,
                tr('Field containing the spatial object id'),
                optional=False,
                parentLayerParameterName=self.SOURCELAYER
            )
        )

        # Parse new parameters
        new_params = self.getAdditionnalParameters()
        if new_params:
            for param in new_params:
                self.addParameter(
                    param['widget'](
                        param['name'],
                        param['label'],
                        optional=param['optional'],
                        parentLayerParameterName=param['parentLayerParameterName'],
                        type=param['type']
                    )
                )

        # OUTPUTS
        # Add output for message
        self.addOutput(
            QgsProcessingOutputString(
                self.OUTPUT_STRING,
                tr('Output message')
            )
        )

    def checkParameterValues(self, parameters, context):

        # Check date has been given
        ok = True
        field_timestamp = self.parameterAsString(parameters, self.FIELD_TIMESTAMP, context)
        manualdate = (self.parameterAsString(parameters, self.MANUALDATE, context)).strip().replace('/', '-')
        if not field_timestamp and not manualdate:
            ok = False
            msg = tr('You need to enter either a date/time field or a manual date/time')

        # check validity of given manual date
        if manualdate:
            ok, msg = validateTimestamp(manualdate)
            if not ok:
                return ok, tr('Manual date or timestamp: ') + msg
            ok = True

        if not ok:
            return False, msg
        return super(ImportObservationData, self).checkParameterValues(parameters, context)

    def getAdditionnalParameters(self):
        """
        Returns a dictionnary of parameters to add dynamically
        Source is the dimensions of the indicator vector field.
        """
        new_params = []

        # Get serie id
        passed_serie = self.getSerieId()
        if not passed_serie or passed_serie <= 0:
            return new_params

        # Get indicator fields data
        id_value_code, id_value_name, id_value_type, id_value_unit = self.getIndicatorFields(passed_serie)

        # Create dynamic parameters
        for i, code in enumerate(id_value_code):
            ptype = QgsProcessingParameterField.Any
            new_params.append(
                {
                    'widget': QgsProcessingParameterField,
                    'name': code,
                    'label': id_value_name[i],
                    'optional': False,
                    'type': ptype,
                    'parentLayerParameterName': self.SOURCELAYER
                }
            )
        return new_params

    @staticmethod
    def getIndicatorFields(given_serie):
        """
        Get indicator data for the given serie id
        """
        # GET INFORMATION of indicator
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        sql = '''
            SELECT id_value_code, id_value_name, id_value_type, id_value_unit
            FROM gobs.indicator AS i
            WHERE id = (
                SELECT s.fk_id_indicator
                FROM gobs.series AS s
                WHERE s.id = {0}
                LIMIT 1
            )
            ;
        '''.format(
            given_serie
        )
        # id_value_code = None
        # id_value_name = None
        # id_value_type = None
        # id_value_unit = None
        try:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if not ok:
                return None
            else:
                # status = 1
                id_value_code = data[0][0]
                id_value_name = data[0][1]
                id_value_type = data[0][2]
                id_value_unit = data[0][3]
        except Exception:
            # status = 0
            return None

        return id_value_code, id_value_name, id_value_type, id_value_unit

    def processAlgorithm(self, parameters, context, feedback):
        # parameters
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')

        # sourcelayer = self.parameterAsVectorLayer(parameters, self.SOURCELAYER, context)
        field_timestamp = self.parameterAsString(parameters, self.FIELD_TIMESTAMP, context)
        manualdate = self.parameterAsString(parameters, self.MANUALDATE, context)
        field_spatial_object = self.parameterAsString(parameters, self.FIELD_SPATIAL_OBJECT, context)
        fields = {}

        # Parse new parameters
        new_params = self.getAdditionnalParameters()
        if new_params:
            for param in new_params:
                fields[param['name']] = self.parameterAsString(parameters, param['name'], context)

        # msg = ''
        # status = 1

        # Get series id from first combo box
        id_serie = self.getSerieId()

        # Import data to temporary table
        feedback.pushInfo(
            tr('IMPORT SOURCE DATA INTO TEMPORARY TABLE')
        )
        temp_schema = 'public'
        temp_table = 'temp_' + str(time.time()).replace('.', '')
        processing.run("qgis:importintopostgis", {
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
            tr('* Source layer has been imported into temporary table')
        )

        # Create import data
        feedback.pushInfo(
            tr('LOG IMPORT INTO import TABLE')
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
                # status = 0
                msg = tr('* The following error has been raised') + '  %s' % error_message
                feedback.reportError(
                    msg
                )
            else:
                # status = 1
                id_import = data[0][0]
                msg = tr('* New import data has been created with ID')
                msg += ' = %s !' % id_import
                feedback.pushInfo(
                    msg
                )
        except Exception:
            # status = 0
            msg = tr('* An unknown error occured while adding import log item')
            feedback.reportError(
                msg
            )

        # GET INFORMATION of indicator
        feedback.pushInfo(
            tr('GET DATA OF RELATED indicator')
        )
        sql = '''
            SELECT id_date_format
            FROM gobs.indicator AS i
            WHERE id = (
                SELECT s.fk_id_indicator
                FROM gobs.series AS s
                WHERE s.id = {0}
                LIMIT 1
            )
            ;
        '''.format(
            id_serie
        )
        id_date_format = None
        try:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            if not ok:
                status = 0
                msg = tr('* The following error has been raised') + '  %s' % error_message
                feedback.reportError(
                    msg
                )
            else:
                status = 1
                id_date_format = data[0][0]
                msg = tr('* Indicator date format is')
                msg += " '%s'" % id_date_format
                feedback.pushInfo(
                    msg
                )
        except Exception:
            status = 0
            msg = tr('* An unknown error occured while getting indicator date format')

        # COPY DATA TO OBSERVATION TABLE
        if status:

            feedback.pushInfo(
                tr('COPY IMPORTED DATA TO observation TABLE')
            )

            # Calculate value for jsonb array destination
            jsonb_array = 'json_build_array('
            a = []
            for name, value in fields.items():
                a.append('s."%s"' % value)
            jsonb_array += ', '.join(a)
            jsonb_array += ')'

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
                INSERT INTO gobs.observation AS o
                (fk_id_series, fk_id_spatial_object, fk_id_import, ob_value, ob_timestamp)
                SELECT
                -- id of the serie
                {id_serie},
                -- id of the spatial object
                so.id,
                -- id of the import log
                {id_import},
                -- jsonb array value computed
                {jsonb_array},
                -- timestamp from the source
                {casted_timestamp}
                FROM "{temp_schema}"."{temp_table}" AS s
                JOIN gobs.spatial_object AS so ON so.so_unique_id = s."{field_spatial_object}"::text

                -- Update line if data already exists
                -- AND data is not validated
                ON CONFLICT ON CONSTRAINT observation_data_unique
                DO UPDATE
                SET (fk_id_import, ob_value) = (EXCLUDED.fk_id_import, EXCLUDED.ob_value)
                WHERE o.ob_validation IS NULL
                ;
            '''.format(
                id_serie=id_serie,
                id_import=id_import,
                jsonb_array=jsonb_array,
                casted_timestamp=casted_timestamp,
                temp_schema=temp_schema,
                temp_table=temp_table,
                field_spatial_object=field_spatial_object
            )
            # print(sql)
            try:
                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    connection_name,
                    sql
                )
                if not ok:
                    status = 0
                    msg = tr('* The following error has been raised') + '  %s' % error_message
                    feedback.reportError(
                        msg + ' \n' + sql
                    )
                else:
                    status = 1
                    msg = tr('* Source data has been successfully imported !')
                    feedback.pushInfo(
                        msg
                    )
            except Exception:
                status = 0
                msg = tr('* An unknown error occured while adding features to spatial_object table')
                feedback.reportError(
                    msg
                )
            finally:

                # Remove temporary table
                feedback.pushInfo(
                    tr('DROP TEMPORARY DATA')
                )
                sql = '''
                    --DROP TABLE IF EXISTS "%s"."%s"
                    SELECT 1;
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
                        tr('* Temporary data has been deleted.')
                    )
                else:
                    feedback.reportError(
                        tr('* An error occured while droping temporary table') + ' "%s"."%s"' % (temp_schema, temp_table)
                    )

            if not status and id_import:
                [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                    connection_name,
                    'DELETE FROM gobs.import WHERE id = %s ' % id_import
                )

            msg = tr('OBSERVATION DATA HAS BEEN SUCCESSFULLY IMPORTED !')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
