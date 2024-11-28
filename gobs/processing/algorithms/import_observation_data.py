__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import time

from typing import Optional, Tuple

import json

import processing

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessing,
    QgsProcessingOutputString,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsProject,
    QgsSettings,
)

from gobs.processing.algorithms.tools import (
    fetch_data_from_sql_query,
    get_postgis_connection_list,
    validateTimestamp,
)
from gobs.qgis_plugin_tools.tools.algorithm_processing import (
    BaseProcessingAlgorithm,
)
from gobs.qgis_plugin_tools.tools.i18n import tr


class ImportObservationData(BaseProcessingAlgorithm):
    SOURCELAYER = 'SOURCELAYER'
    MANUAL_START_DATE = 'MANUAL_START_DATE'
    MANUAL_END_DATE = 'MANUAL_END_DATE'
    FIELD_START_TIMESTAMP = 'FIELD_START_TIMESTAMP'
    FIELD_END_TIMESTAMP = 'FIELD_END_TIMESTAMP'
    FIELD_SPATIAL_OBJECT = 'FIELD_SPATIAL_OBJECT'
    FIELDS = 'FIELDS'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    DATE_FIELDS = {
        'Start': {
            'field': FIELD_START_TIMESTAMP,
            'manual': MANUAL_START_DATE
        },
        'End': {
            'field': FIELD_END_TIMESTAMP,
            'manual': MANUAL_END_DATE
        }
    }

    def name(self):
        return 'import_observation_data'

    def displayName(self):
        return tr('Import observation data')

    def group(self):
        return tr('Import')

    def groupId(self):
        return 'gobs_import'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm allows to import observation data from a QGIS vector or table layer into the G-Obs database'
            '\n'
            '\n'
            'The G-Obs administrator must have created needed series beforehand by adding the required items '
            'in the related database tables: gobs.protocol, gobs.indicator, gobs.actor and gobs.spatial_layer.'
            '\n'
            'Source data: choose the QGIS vector or table layer containing the observation data you want to import into the chosen series.'
            '\n'
            'Each feature of this source layer is an observation, characterized by a spatial object, a timestamp, a vector of values, '
            'and will be imported into the database table gobs.observation.'
            '\n'
            '* Date time fields: choose the field containing the exact date or date & time of each observation: '
            'start and (optional) end timestamp'
            ' Leave empty if all the features share the same date/time.'
            ' This field must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
            '* Manual dates or timestamps: if all the data share the same timestamp, you can enter the exact value. '
            'For example, 2020 if all the observation concern the population of the cities in the year 2020.'
            ' This field must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
            '* Field containing the spatial object id: '
            'choose the field containing the unique identifier of the related spatial object in the spatial layer of this series. '
            ' (its value will be stored in the column "so_unique_id" in the "spatial_object" table)'
            '\n'
            '* Depending of the chose series, you will need to choose the fields containing '
            'the data of each dimension of the observation vector of values.'
        )
        return short_help

    def getSeriesId(self):
        """
        Get the serie ID
        To be overriden by child instances
        """
        return 0

    def getSeriesDefaultValues(self):
        """
        Get the dictionary of default values to apply to the fields
        """
        return {}

    def initAlgorithm(self, config):
        # INPUTS
        # Source layer
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SOURCELAYER,
                tr('Source data'),
                optional=False,
                types=[QgsProcessing.TypeVector]
            )
        )
        for k, v in self.DATE_FIELDS.items():
            # Date field
            self.addParameter(
                QgsProcessingParameterField(
                    v['field'],
                    tr(k) + ' ' + tr('date and time field. ISO Format'),
                    optional=True,
                    parentLayerParameterName=self.SOURCELAYER
                )
            )
            # Manual date field
            self.addParameter(
                QgsProcessingParameterString(
                    v['manual'],
                    tr(k) + ' ' + tr('manual date or timestamp, (2019-01-06 or 2019-01-06 22:59:50) Use when the data refers to only one date or time'),
                    optional=True
                )
            )

        # Spatial object id field
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_SPATIAL_OBJECT,
                tr('Field containing the spatial object id (its value will be stored in the column "so_unique_id" in the "spatial_object" table)'),
                optional=False,
                parentLayerParameterName=self.SOURCELAYER
            )
        )

        # Parse new parameters
        project = QgsProject.instance()
        new_params = self.get_additional_parameters(project)
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

        # Check that the connection name has been configured
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        if not connection_name:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        if connection_name not in get_postgis_connection_list():
            return False, tr('The configured connection name does not exists in QGIS')

        # Check date has been given
        ok = True
        for k, v in self.DATE_FIELDS.items():
            field_timestamp = self.parameterAsString(parameters, v['field'], context)
            manualdate = (self.parameterAsString(parameters, v['manual'], context)).strip().replace('/', '-')
            if k == 'Start' and not field_timestamp and not manualdate:
                ok = False
                msg = tr(k) + ' - ' + tr('You need to enter either a date/time field or a manual date/time')

            # check validity of given manual date
            if manualdate:
                ok, msg = validateTimestamp(manualdate)
                if not ok:
                    return ok, tr(k) + ' - ' + tr('Manual date or timestamp: ') + msg
                ok = True

            if not ok:
                return False, msg

        # Additionnal checks
        # TODO

        return super(ImportObservationData, self).checkParameterValues(parameters, context)

    def get_additional_parameters(self, project):
        """
        Returns a dictionary of parameters to add dynamically
        Source is the dimensions of the indicator vector field.
        """

        # Get series id
        passed_series = self.getSeriesId()
        if not passed_series or passed_series <= 0:
            return []

        # Get indicator fields data
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        id_value_code, id_value_name, id_value_type, id_value_unit = self.get_indicator_fields(
            connection_name, passed_series)

        if not id_value_code:
            return []

        new_params = []

        # Create dynamic parameters
        for i, code in enumerate(id_value_code):
            field_params = {
                'widget': QgsProcessingParameterField,
                'name': code,
                'label': id_value_name[i],
                'optional': False,
                'type': QgsProcessingParameterField.Any,
                'parentLayerParameterName': self.SOURCELAYER
            }

            new_params.append(field_params)

        return new_params

    @staticmethod
    def get_indicator_fields(connection_name, given_series) -> Optional[Tuple[str, str, str, str]]:
        """
        Get indicator data for the given series id
        """
        # GET INFORMATION of indicator
        separator = '#!#'
        sql = f'''
            SELECT
                array_to_string(array_agg(d.di_code), '{separator}'),
                array_to_string(array_agg(d.di_label), '{separator}'),
                array_to_string(array_agg(d.di_type), '{separator}'),
                array_to_string(array_agg(d.di_unit), '{separator}')
            FROM gobs.indicator AS i
            INNER JOIN gobs.dimension AS d
                ON d.fk_id_indicator = i.id
            WHERE i.id = (
                SELECT s.fk_id_indicator
                FROM gobs.series AS s
                WHERE s.id = {given_series}
                LIMIT 1
            )
            ;
        '''

        # noinspection PyBroadException
        try:
            data, error = fetch_data_from_sql_query(connection_name, sql)
            if error:
                return None
            id_value_code = data[0][0].split(separator)
            id_value_name = data[0][1].split(separator)
            id_value_type = data[0][2].split(separator)
            id_value_unit = data[0][3].split(separator)
        except Exception:
            return None

        return id_value_code, id_value_name, id_value_type, id_value_unit

    def processAlgorithm(self, parameters, context, feedback):
        # parameters
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')

        field_spatial_object = self.parameterAsString(parameters, self.FIELD_SPATIAL_OBJECT, context)
        new_params_values = []

        # Parse new parameters
        # Add values in the correct order
        new_params = self.get_additional_parameters(context.project())

        # Get series id from first combo box
        id_series = self.getSeriesId()

        # Store values for indicator dimension fields
        s = QgsSettings()
        last_indicator_fields = s.value("gobs/last_indicator_fields", "{}")
        series_default_values = {}
        if last_indicator_fields != '{}':
            default_values = json.loads(last_indicator_fields)

        input_fields = (
            self.SOURCELAYER, self.MANUAL_START_DATE, self.MANUAL_END_DATE,
            self.FIELD_START_TIMESTAMP, self.FIELD_END_TIMESTAMP, self.FIELD_SPATIAL_OBJECT
        )
        for field in input_fields:
            series_default_values[field] = self.parameterAsString(parameters, field, context)

        if new_params:
            for param in new_params:
                param_value = self.parameterAsString(parameters, param['name'], context)
                new_params_values.append(param_value)
                series_default_values[param['name']] = param_value

        # Set default values
        default_values[id_series] = series_default_values
        s.setValue("gobs/last_indicator_fields", json.dumps(default_values))

        msg = ''
        status = 1

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
        ''' % id_series
        id_import = None

        try:
            data, error = fetch_data_from_sql_query(connection_name, sql)
            if error:
                msg = tr('* The following error has been raised') + '  %s' % error
                feedback.reportError(
                    msg
                )
            else:
                id_import = data[0][0]
                msg = tr('* New import data has been created with ID')
                msg+= ' = %s !' % id_import
                feedback.pushInfo(
                    msg
                )
        except Exception:
            msg = tr('* An unknown error occurred while adding import log item')
            feedback.reportError(
                msg
            )

        # GET INFORMATION of indicator
        feedback.pushInfo(
            tr('GET DATA OF RELATED indicator')
        )
        sql = '''
            SELECT id_date_format, array_to_string(array_agg(d.di_type), ',')
            FROM gobs.indicator AS i
            INNER JOIN gobs.dimension AS d
                ON d.fk_id_indicator = i.id
            WHERE i.id = (
                SELECT s.fk_id_indicator
                FROM gobs.series AS s
                WHERE s.id = {0}
                LIMIT 1
            )
            GROUP BY id_date_format
            ;
        '''.format(
            id_series
        )
        id_date_format = None
        id_value_types = None
        try:
            data, error = fetch_data_from_sql_query(connection_name, sql)
            if error:
                status = 0
                msg = tr('* The following error has been raised') + '  %s' % error
                feedback.reportError(
                    msg
                )
            else:
                status = 1
                id_date_format = data[0][0]
                id_value_types = data[0][1].split(',')
                msg = tr('* Indicator date format is')
                msg+= " '%s'" % id_date_format
                feedback.pushInfo(
                    msg
                )
        except Exception as e:
            status = 0
            msg = tr('* An unknown error occured while getting indicator date format')
            feedback.reportError(
                msg + ' ' + str(e)
            )

        # COPY DATA TO OBSERVATION TABLE
        if status:

            feedback.pushInfo(
                tr('COPY IMPORTED DATA TO observation TABLE')
            )

            # Calculate value for jsonb array destination
            jsonb_array = 'json_build_array('
            jsonb_array_list = []
            for i, fieldname in enumerate(new_params_values):
                id_value_type = id_value_types[i]
                convertor_a = ''
                convertor_b = ''
                if id_value_type in ('integer', 'real'):
                    # remove useless spaces if data is supposed to be integer or real
                    convertor_a = "regexp_replace("
                    convertor_b = ", '[^0-9,\.\-]', '', 'g')"  # NOQA
                vector_value = '{a}trim(s."{fieldname}"::text){b}::{value_type}'.format(
                    a=convertor_a,
                    fieldname=fieldname,
                    b=convertor_b,
                    value_type=id_value_type
                )

                jsonb_array_list.append(vector_value)
            jsonb_array+= ', '.join(jsonb_array_list)
            jsonb_array+= ')'

            # Use the correct expression for casting date and/or time
            caster = 'timestamp'
            if id_date_format in ('year', 'month', 'day'):
                caster = 'date'
            casted_timestamp = {}
            for k, v in self.DATE_FIELDS.items():
                field_timestamp = self.parameterAsString(parameters, v['field'], context)
                manualdate = (self.parameterAsString(parameters, v['manual'], context)).strip().replace('/', '-')

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
                    casted_timestamp[k] = '''
                        '{0}'::{1}
                    '''.format(
                        manualdate,
                        caster
                    )
                else:
                    if field_timestamp:
                        casted_timestamp_text = ''
                        if id_date_format == 'year':
                            casted_timestamp_text = '''
                                concat( trim(s."{0}"::text), '-01-01')::{1}
                            '''.format(
                                field_timestamp,
                                caster
                            )
                        else:
                            casted_timestamp_text = '''
                                date_trunc('{0}', s."{1}"::{2})
                            '''.format(
                                id_date_format,
                                field_timestamp,
                                caster
                            )
                        casted_timestamp[k] = casted_timestamp_text
                    else:
                        casted_timestamp[k] = 'NULL'

            # We use the unique constraint to override or not the data
            # "observation_data_unique" UNIQUE CONSTRAINT, btree (fk_id_series, fk_id_spatial_object, ob_start_timestamp)
            # ob_validation is automatically set by the trigger gobs.trg_after_import_validation()
            # to now() when the import is validated
            sql = '''
                INSERT INTO gobs.observation AS o (
                    fk_id_series, fk_id_spatial_object, fk_id_import,
                    ob_value, ob_start_timestamp, ob_end_timestamp
                )
                SELECT
                -- id of the serie
                {id_series},
                -- id of the spatial object
                so.id,
                -- id of the import log
                {id_import},
                -- jsonb array value computed
                {jsonb_array},
                -- start timestamp from the source
                {casted_timestamp_start},
                -- end timestamp from the source
                {casted_timestamp_end}
                FROM "{temp_schema}"."{temp_table}" AS s
                JOIN gobs.spatial_object AS so
                    ON True
                    AND so.fk_id_spatial_layer = (
                        SELECT fk_id_spatial_layer FROM gobs.series WHERE id = {id_series}
                    )
                    AND so.so_unique_id = s."{field_spatial_object}"::text
                    AND (
                        (so.so_valid_from IS NULL OR so.so_valid_from <= {casted_timestamp_start}::date)
                        AND
                        (so.so_valid_to IS NULL OR so.so_valid_to > {casted_timestamp_start}::date)
                    )
            '''.format(
                id_series=id_series,
                id_import=id_import,
                jsonb_array=jsonb_array,
                casted_timestamp_start=casted_timestamp['Start'],
                casted_timestamp_end=casted_timestamp['End'],
                temp_schema=temp_schema,
                temp_table=temp_table,
                field_spatial_object=field_spatial_object
            )
            # If end date field or manual date is given, use it in the JOIN too
            if casted_timestamp['End'] != 'NULL':
                sql += '''
                    AND (
                        (so.so_valid_from IS NULL OR so.so_valid_from <= {casted_timestamp_end}::date)
                        AND
                        (so.so_valid_to IS NULL OR so.so_valid_to > {casted_timestamp_end}::date)
                    )
                '''.format(
                    casted_timestamp_end=casted_timestamp['End'],
                )
            # Manage INSERT conflicts
            # If the observation has the same id_series, same start timestamp and same spatial object
            # The observation is modified with the new end timestamp and ob_value
            # This means a new observation is created when the start timestamp is different for the same series id and spatial object
            sql += '''
                -- Update line if data already exists
                -- AND data is not validated
                ON CONFLICT ON CONSTRAINT observation_data_unique
                DO UPDATE
                SET (fk_id_import, ob_value, ob_end_timestamp) = (EXCLUDED.fk_id_import, EXCLUDED.ob_value, EXCLUDED.ob_end_timestamp)
                WHERE o.ob_validation IS NULL
            '''
            feedback.pushInfo(sql)
            try:
                _, error = fetch_data_from_sql_query(connection_name, sql)
                if error:
                    status = 0
                    msg = tr('* The following error has been raised') + '  %s' % error
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
                msg = tr('* An unknown error occurred while adding features to spatial_object table')
                feedback.reportError(
                    msg
                )
            finally:

                # Remove temporary table
                remove_temp = True
                if remove_temp:
                    feedback.pushInfo(
                        tr('DROP TEMPORARY DATA')
                    )
                    sql = '''
                        DROP TABLE IF EXISTS "%s"."%s"
                    ;
                    ''' % (
                        temp_schema,
                        temp_table
                    )
                    _, error = fetch_data_from_sql_query(connection_name, sql)
                    if not error:
                        feedback.pushInfo(
                            tr('* Temporary data has been deleted.')
                        )
                    else:
                        feedback.reportError(
                            tr('* An error occurred while dropping temporary table') + ' "%s"."%s"' % (temp_schema, temp_table)
                        )

            if not status and id_import:
                fetch_data_from_sql_query(
                    connection_name,
                    'DELETE FROM gobs.import WHERE id = %s ' % id_import
                )

            msg = tr('OBSERVATION DATA HAS BEEN SUCCESSFULLY IMPORTED !')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
