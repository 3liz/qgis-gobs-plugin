__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import os
import time

import processing

from qgis.core import (
    Qgis,
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingOutputString,
    QgsProcessingParameterEnum,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
    QgsProject,
    QgsWkbTypes,
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


class ImportSpatialLayerData(BaseProcessingAlgorithm):

    SPATIALLAYER = 'SPATIALLAYER'
    ACTOR = 'ACTOR'
    SOURCELAYER = 'SOURCELAYER'
    UNIQUEID = 'UNIQUEID'
    UNIQUELABEL = 'UNIQUELABEL'
    DATE_VALIDITY_MIN = 'DATE_VALIDITY_MIN'
    MANUAL_DATE_VALIDITY_MIN = 'MANUAL_DATE_VALIDITY_MIN'
    DATE_VALIDITY_MAX = 'DATE_VALIDITY_MAX'
    MANUAL_DATE_VALIDITY_MAX = 'MANUAL_DATE_VALIDITY_MAX'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    SPATIALLAYERS = []
    ACTORS = []

    def name(self):
        return 'import_spatial_layer_data'

    def displayName(self):
        return tr('Import spatial layer data')

    def group(self):
        return tr('Import')

    def groupId(self):
        return 'gobs_import'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm allows to import data from a QGIS spatial layer into the G-Obs database'
            '\n'
            '\n'
            'The G-Obs administrator must have created the needed spatial layer beforehand by addind the required items in the related database tables: gobs.actor_category, gobs.actor and gobs.spatial_layer.'
            '\n'
            '* Target spatial layer: choose one of the spatial layers available in G-Obs database'
            '\n'
            '* Source actor: choose the actor among the pre-defined list of actors'
            '\n'
            '* Source data: choose the QGIS vector layer containing the spatial data you want to import into the chosen spatial layer.'
            '\n'
            '* Unique identifier: choose the field containing the unique ID. It can be an integer or a text field, but must be unique.'
            '\n'
            '* Unique label: choose the text field containing the unique label of the layer feature. You could use the QGIS field calculator to create one if needed.'
            '\n'
            '* Start of validity: choose the field with the start timestamp of validity for each feature.'
            ' Leave empty if all the features share the same date/time and manually enter the value in the next input.'
            ' This field content must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
            '* Start of validity for all features'
            ' Specify the start timestamp of validity for all the objects in the spatial layer.'
            ' This value must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
            '* End of validity: choose the field with the end timestamp of validity for each feature.'
            ' Leave empty if all the features share the same date/time and manually enter the value in the next input.'
            ' This field content must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
            '* End of validity for all features'
            ' Specify the end timestamp of validity for all the objects in the spatial layer.'
            ' This value must respect the ISO format. For example 2020-05-01 10:50:30 or 2020-01-01'
            '\n'
        )
        return short_help

    def initAlgorithm(self, config):
        # INPUTS
        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        if not connection_name:
            connection_name = os.environ.get("GOBS_CONNECTION_NAME")
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # List of spatial_layer
        sql = '''
            SELECT id, sl_label
            FROM gobs.spatial_layer
            ORDER BY sl_label
        '''
        data = []
        if get_data == 'yes' and connection_name in get_postgis_connection_list():
            data, _ = fetch_data_from_sql_query(connection_name, sql)
        self.SPATIALLAYERS = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPATIALLAYER,
                tr('Target spatial layer'),
                options=self.SPATIALLAYERS,
                optional=False
            )
        )

        # List of actors
        sql = '''
            SELECT id, a_label
            FROM gobs.actor
            ORDER BY a_label
        '''
        data = []
        if get_data == 'yes' and connection_name in get_postgis_connection_list():
            data, _ = fetch_data_from_sql_query(connection_name, sql)
        self.ACTORS = ['%s - %s' % (a[1], a[0]) for a in data]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ACTOR,
                tr('Source actor'),
                options=self.ACTORS,
                optional=False
            )
        )

        # Source layer
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.SOURCELAYER,
                tr('Source data'),
                optional=False
            )
        )

        # Unique identifier
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUEID,
                tr('Unique identifier'),
                parentLayerParameterName=self.SOURCELAYER
            )
        )

        # Unique label
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUELABEL,
                tr('Unique label'),
                parentLayerParameterName=self.SOURCELAYER,
                type=QgsProcessingParameterField.String
            )
        )

        # Min validity field
        self.addParameter(
            QgsProcessingParameterField(
                self.DATE_VALIDITY_MIN,
                tr('Start timestamp of validity. Field in ISO Format'),
                optional=True,
                parentLayerParameterName=self.SOURCELAYER
            )
        )

        # Manual min validity
        self.addParameter(
            QgsProcessingParameterString(
                self.MANUAL_DATE_VALIDITY_MIN,
                tr('Manual start timestamp of validity (2019-01-06 or 2019-01-06 22:59:50)'),
                optional=True
            )
        )

        # Max validity field
        self.addParameter(
            QgsProcessingParameterField(
                self.DATE_VALIDITY_MAX,
                tr('End timestamp of validity. Field in ISO Format'),
                optional=True,
                parentLayerParameterName=self.SOURCELAYER
            )
        )

        # Manual max validity
        self.addParameter(
            QgsProcessingParameterString(
                self.MANUAL_DATE_VALIDITY_MAX,
                tr('Manual end timestamp of validity (2019-01-31 or 2019-01-31 23:59:59)'),
                optional=True
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
        connection_name_env = os.environ.get("GOBS_CONNECTION_NAME")
        if not connection_name and not connection_name_env:
            return False, tr('You must use the "Configure G-obs plugin" alg to set the database connection name')

        # Check that it corresponds to an existing connection
        if connection_name and connection_name not in get_postgis_connection_list():
            return False, tr('The configured connection name does not exists in QGIS')

        # replace connection_name by env variable
        if not connection_name:
            connection_name = connection_name_env

        # Check correct validity timestamps have been given
        date_fields = {
            'Start of validity': {
                'field': self.DATE_VALIDITY_MIN,
                'manual': self.MANUAL_DATE_VALIDITY_MIN,
                'optional': False
            },
            'End of validity': {
                'field': self.DATE_VALIDITY_MAX,
                'manual': self.MANUAL_DATE_VALIDITY_MAX,
                'optional': True
            }
        }
        for key in date_fields:
            ok = True
            item = date_fields[key]
            field_timestamp = self.parameterAsString(parameters, item['field'], context)
            manualdate = (self.parameterAsString(parameters, item['manual'], context)).strip().replace('/', '-')
            if not field_timestamp and not manualdate and not item['optional']:
                ok = False
                msg = tr(key) + ' - '
                msg += tr('You need to enter either a timestamp field or a manual timestamp')

            # check validity of given manual date
            if manualdate:
                ok, msg = validateTimestamp(manualdate)
                if not ok:
                    return False, tr(key) + ' - ' + msg
                ok = True

            if not ok:
                return False, msg

        return super(ImportSpatialLayerData, self).checkParameterValues(parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        # parameters
        # Database connection parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        if not connection_name:
            connection_name = os.environ.get("GOBS_CONNECTION_NAME")

        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        actor = self.ACTORS[parameters[self.ACTOR]]
        sourcelayer = self.parameterAsVectorLayer(parameters, self.SOURCELAYER, context)
        uniqueid = self.parameterAsString(parameters, self.UNIQUEID, context)
        uniquelabel = self.parameterAsString(parameters, self.UNIQUELABEL, context)
        date_validity_min = self.parameterAsString(parameters, self.DATE_VALIDITY_MIN, context)
        manual_date_validity_min = self.parameterAsString(parameters, self.MANUAL_DATE_VALIDITY_MIN, context)
        date_validity_max = self.parameterAsString(parameters, self.DATE_VALIDITY_MAX, context)
        manual_date_validity_max = self.parameterAsString(parameters, self.MANUAL_DATE_VALIDITY_MAX, context)

        msg = ''
        status = 1

        # Get chosen spatial layer id
        id_spatial_layer = spatiallayer.split('-')[-1].strip()

        # Get chosen actor id
        id_actor = actor.split('-')[-1].strip()

        feedback.pushInfo(
            tr('CHECK COMPATIBILITY BETWEEN SOURCE AND TARGET GEOMETRY TYPES')
        )
        # Get spatial layer geometry type
        sql = '''
        SELECT sl_geometry_type
        FROM gobs.spatial_layer
        WHERE id = {0}
        LIMIT 1
        '''.format(
            id_spatial_layer
        )
        target_type = None
        data, error = fetch_data_from_sql_query(connection_name, sql)
        if error:
            msg = tr('* The following error has been raised') + '  %s' % error
            feedback.reportError(
                msg
            )
            raise QgsProcessingException(msg)
        else:
            for line in data:
                target_type = line[0].lower()

        # Check multi type
        target_is_multi = target_type.startswith('multi')

        # Get vector layer geometry type
        # And compare it with the spatial_layer type
        if Qgis.versionInt() < 33400:
            source_type = QgsWkbTypes.geometryDisplayString(int(sourcelayer.geometryType())).lower()
            source_wtype = QgsWkbTypes.displayString(int(sourcelayer.wkbType())).lower()
        else:
            source_type = QgsWkbTypes.geometryDisplayString(sourcelayer.geometryType()).lower()
            source_wtype = QgsWkbTypes.displayString(sourcelayer.wkbType()).lower()

        if not target_type.endswith(source_type):
            msg = tr('Source vector layer and target spatial layer do not have compatible geometry types')
            msg+= ' - SOURCE: {}, TARGET: {}'.format(
                source_type, target_type
            )
            feedback.pushInfo(msg)
            raise QgsProcessingException(msg)

        source_is_multi = source_wtype.startswith('multi')

        # Cannot import multi type into single type target spatial layer
        if source_is_multi and not target_is_multi:
            msg = tr('Cannot import a vector layer with multi geometries into a target spatial layer with a simple geometry type defined')
            msg+= ' - SOURCE: {}, TARGET: {}'.format(
                source_wtype, target_type
            )
            feedback.pushInfo(msg)
            raise QgsProcessingException(msg)

        # Import data to temporary table
        feedback.pushInfo(
            tr('IMPORT SOURCE LAYER INTO TEMPORARY TABLE')
        )
        temp_schema = 'public'
        temp_table = 'temp_' + str(time.time()).replace('.', '')
        processing.run("qgis:importintopostgis", {
            'INPUT': parameters[self.SOURCELAYER],
            'DATABASE': connection_name,
            'SCHEMA': temp_schema,
            'TABLENAME': temp_table,
            'PRIMARY_KEY': 'gobs_id',
            'GEOMETRY_COLUMN': 'geom',
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
        # Add ST_Multi if needed
        st_multi_left = ''
        st_multi_right = ''
        if target_is_multi:
            st_multi_left = 'ST_Multi('
            st_multi_right = ')'

        # Get target geometry type in integer
        geometry_type_integer = 1
        if target_type.replace('multi', '') == 'linestring':
            geometry_type_integer = 2
        if target_type.replace('multi', '') == 'polygon':
            geometry_type_integer = 3

        # Format validity timestamp fields
        if manual_date_validity_min.strip():
            manualdate = manual_date_validity_min.strip().replace('/', '-')
            casted_timestamp_min = '''
                '{0}'::timestamp
            '''.format(manualdate)
        else:
            casted_timestamp_min = '''
                s."{0}"::timestamp
            '''.format(date_validity_min)

        has_max_validity = False
        if manual_date_validity_max.strip() or date_validity_max:
            has_max_validity = True
            if manual_date_validity_max.strip():
                manualdate = manual_date_validity_max.strip().replace('/', '-')
                casted_timestamp_max = '''
                    '{0}'::timestamp
                '''.format(manualdate)
            else:
                casted_timestamp_max = '''
                    s."{0}"::timestamp
                '''.format(date_validity_max)

        # Copy data to spatial_object
        feedback.pushInfo(
            tr('COPY IMPORTED DATA TO spatial_object')
        )
        sql = '''
            INSERT INTO gobs.spatial_object (
                so_unique_id, so_unique_label,
                geom,
                fk_id_spatial_layer,
                fk_id_actor,
                so_valid_from,
            '''
        if has_max_validity:
            sql += ', so_valid_to'
        sql += '''
            )
            SELECT
                "{so_unique_id}", "{so_unique_label}",
                {st_multi_left}ST_Transform(ST_CollectionExtract(ST_MakeValid(geom),{geometry_type_integer}), 4326){st_multi_right} AS geom,
                {id_spatial_layer},
                {id_actor},
                {casted_timestamp_min}
        '''.format(
            so_unique_id=uniqueid,
            so_unique_label=uniquelabel,
            st_multi_left=st_multi_left,
            geometry_type_integer=geometry_type_integer,
            st_multi_right=st_multi_right,
            id_spatial_layer=id_spatial_layer,
            id_actor=id_actor,
            casted_timestamp_min=casted_timestamp_min
        )
        if has_max_validity:
            sql += ', {casted_timestamp_max}'.format(
                casted_timestamp_max=casted_timestamp_max
            )
        sql += '''
            FROM "{temp_schema}"."{temp_table}" AS s

            -- Update line if data already exists
            -- i.e. Same external ids for the same layer and the same start validity date
            -- so_unique_id, fk_id_spatial_layer AND so_valid_from are the same
            -- This is considered as the same object as the one already in database
            -- We update the geometry, label, end date of validity, actor ID
            ON CONFLICT
                ON CONSTRAINT spatial_object_unique_key
            DO UPDATE
            SET (geom, so_unique_label, so_valid_to, fk_id_actor) =
            (EXCLUDED.geom, EXCLUDED.so_unique_label, EXCLUDED.so_valid_to, EXCLUDED.fk_id_actor)
            WHERE True
            ;

        '''.format(
            temp_schema=temp_schema,
            temp_table=temp_table
        )

        try:
            _, error = fetch_data_from_sql_query(connection_name, sql)
            if error:
                status = 0
                msg = tr('* The following error has been raised') + '  %s' % error
                feedback.reportError(
                    msg
                )
                feedback.pushInfo(sql)
            else:
                status = 1
                msg = tr('* Source data has been successfully imported !')
                feedback.pushInfo(
                    msg
                )
        except Exception as e:
            status = 0
            msg = tr('* An unknown error occured while adding features to spatial_object table')
            msg+= ' ' + str(e)

        # Check there is no issues with related observation data
        # For each series related to the chosen spatial layer
        # SELECT gobs.find_observation_with_wrong_spatial_object({fk_id_series})
        # v1/ Only check and display warning
        # v2/ Check and try to update with gobs.update_observations_with_wrong_spatial_objects
        # v3/ Find orphans

        # Remove temporary table
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

        msg = tr('SPATIAL LAYER HAS BEEN SUCCESSFULLY IMPORTED !')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
