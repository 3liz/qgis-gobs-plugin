__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"


import re

from qgis.core import (
    QgsExpressionContextUtils,
    QgsProcessingException,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterEnum,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProject,
)

from gobs.processing.algorithms.get_data_as_layer import GetDataAsLayer
from gobs.processing.algorithms.tools import (
    fetch_data_from_sql_query,
    get_postgis_connection_list,
    validateTimestamp,
)
from gobs.qgis_plugin_tools.tools.i18n import tr


class GetSpatialLayerVectorData(GetDataAsLayer):

    SPATIALLAYER = 'SPATIALLAYER'
    SPATIALLAYER_ID = 'SPATIALLAYER_ID'
    GEOM_FIELD = 'geom'
    VALIDITY_DATE = 'VALIDITY_DATE'

    def name(self):
        return 'get_spatial_layer_vector_data'

    def displayName(self):
        return tr('Get spatial layer vector data')

    def group(self):
        return tr('Tools')

    def groupId(self):
        return 'gobs_tools'

    def shortHelpString(self):
        short_help = tr(
            'This algorithm allows to add a vector layer in your QGIS project containing the spatial data '
            'from the chosen G-Obs spatial layer. Data are dynamically fetched from the database, '
            'meaning they are always up-to-date.'
            '\n'
            '* Name of the output layer: choose the name of the QGIS layer to create. '
            'If not given, the label of the spatial layer will be used.'
            '\n'
            '* Spatial layer: choose the G-Obs spatial layer you want to use as the data source.'
            '\n'
            '* Date of validity: if you want to see the data for a specific date (ex: today or 2010-01-01)'
        )
        return short_help

    def initAlgorithm(self, config):

        # use parent class to get other parameters
        super(self.__class__, self).initAlgorithm(config)

        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        # Add spatial layer choice
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
        self.SPATIALLAYERS_DICT = {a[0]: a[1] for a in data}
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPATIALLAYER,
                tr('Spatial layer'),
                options=self.SPATIALLAYERS,
                optional=False
            )
        )

        # Id of spatial layer, to get the layer directly
        # mainly used from other processing algs
        p = QgsProcessingParameterNumber(
            self.SPATIALLAYER_ID,
            tr('Spatial layer ID. If given, it overrides previous choice'),
            optional=True,
            defaultValue=-1
        )
        p.setFlags(QgsProcessingParameterDefinition.FlagHidden)
        self.addParameter(p)

        # Validity date
        self.addParameter(
            QgsProcessingParameterString(
                self.VALIDITY_DATE,
                tr('View data for a specific date (ex: today or 2010-01-01)'),
                optional=True
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

        spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)

        # Check layyer id is in the list of existing spatial layers
        if spatial_layer_id and spatial_layer_id > 0:
            if spatial_layer_id not in self.SPATIALLAYERS_DICT:
                return False, tr('Spatial layer ID does not exists in the database')

        # check validity of given manual date
        validity_date = (self.parameterAsString(parameters, self.VALIDITY_DATE, context)).strip().replace('/', '-')
        if validity_date:
            ok, msg = validateTimestamp(validity_date)
            if not ok and validity_date != 'today':
                return False, tr('View data for a specific date') + ': ' + msg
            ok = True

        return super(GetSpatialLayerVectorData, self).checkParameterValues(parameters, context)

    def setSql(self, parameters, context, feedback):

        # Database connection parameters
        connection_name = QgsExpressionContextUtils.projectScope(context.project()).variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')
        if get_data != 'yes':
            return

        # Get id, label and geometry type from chosen spatial layer
        spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
        id_spatial_layer = int(spatiallayer.split('-')[-1].strip())

        # Override spatial layer id from second number input
        spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)
        if spatial_layer_id and spatial_layer_id in self.SPATIALLAYERS_DICT:
            id_spatial_layer = spatial_layer_id

        # Get only data in validity date
        validity_date = (self.parameterAsString(parameters, self.VALIDITY_DATE, context)).strip().replace('/', '-')

        feedback.pushInfo(
            tr('GET DATA FROM CHOSEN SPATIAL LAYER')
        )
        sql = "SELECT id, sl_label, sl_geometry_type FROM gobs.spatial_layer WHERE id = %s" % id_spatial_layer
        data, error = fetch_data_from_sql_query(connection_name, sql)
        if not error:
            label = data[0][1]
            message = tr('* Data has been fetched for spatial layer')
            message += ' %s !' % label
            feedback.pushInfo(
                message
            )
        else:
            raise QgsProcessingException(error)

        # Retrieve needed data
        id_spatial_layer = data[0][0]
        geometry_type = data[0][2]

        # Build SQL
        sql = '''
            SELECT
            id,
            so_unique_id AS code,
            so_unique_label AS label,
            so_valid_from AS valid_from,
            so_valid_to AS valid_to,
            geom::geometry({1}, 4326) AS geom
            FROM gobs.spatial_object
            WHERE fk_id_spatial_layer = {0}
        '''.format(
            id_spatial_layer,
            geometry_type
        )
        # View the spatial object for a specific day.
        # only if validity date is given
        if validity_date:
            if validity_date != 'today':
                # keep only date (remove time)
                validity_date = validity_date[0:10]
                # test format and complete if necessary
                p = re.compile('^[0-9]{4}$')
                if p.match(validity_date):
                    validity_date = '%s-01-01' % validity_date
                p = re.compile('^[0-9]{4}-[0-9]{2}$')
                if p.match(validity_date):
                    validity_date = '%s-01' % validity_date
            p = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
            if validity_date == 'today' or p.match(validity_date):
                sql += '''
            AND (
                (so_valid_from IS NULL OR so_valid_from <= '{validity_date}'::date)
                AND
                (so_valid_to IS NULL OR so_valid_to > '{validity_date}'::date)
            )
                '''.format(
                    validity_date=validity_date
                )

        # Format SQL
        line_break = '''
'''
        spaces = 12 * ' '
        sql_log = sql.replace(spaces, '').replace(line_break + line_break, line_break)
        feedback.pushInfo('SQL = \n' + sql_log)

        self.SQL = sql_log.replace('\n', ' ').replace(line_break, ' ').rstrip(';')

    def setLayerName(self, parameters, context, feedback):

        # Name given by the user
        output_layer_name = parameters[self.OUTPUT_LAYER_NAME]

        # Default name if nothing given
        if not output_layer_name.strip():
            # Get spatial layer id from first combo box
            spatiallayer = self.SPATIALLAYERS[parameters[self.SPATIALLAYER]]
            id_spatial_layer = int(spatiallayer.split('-')[-1].strip())

            # Override spatial layer id from second number input
            spatial_layer_id = self.parameterAsInt(parameters, self.SPATIALLAYER_ID, context)
            if spatial_layer_id and spatial_layer_id in self.SPATIALLAYERS_DICT:
                id_spatial_layer = spatial_layer_id

            output_layer_name = self.SPATIALLAYERS_DICT[id_spatial_layer]

        # Set layer name
        self.LAYER_NAME = output_layer_name
