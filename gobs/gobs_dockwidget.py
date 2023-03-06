__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import webbrowser

from functools import partial
from typing import Tuple

from processing import execAlgorithmDialog
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsExpressionContextUtils,
    QgsProject,
)
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
)

from gobs.plugin_tools import available_migrations, format_version_integer
from gobs.processing.algorithms.import_observation_data import (
    ImportObservationData,
)
from gobs.processing.algorithms.tools import (
    fetch_data_from_sql_query,
    get_postgis_connection_list,
)
from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.resources import load_ui
from gobs.qgis_plugin_tools.tools.version import version

FORM_CLASS = load_ui('gobs_dockwidget_base.ui')


class GobsDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(GobsDockWidget, self).__init__(parent)

        self.iface = iface
        self.setupUi(self)

        # Buttons directly linked to an algorithm
        self.algorithms = [
            'configure_plugin',
            'create_database_structure',
            'upgrade_database_structure',

            'create_database_local_interface',

            'import_spatial_layer_data',

            'get_spatial_layer_vector_data',
            'get_series_data',
            'get_series_list',
            'get_aggregated_data',

            'remove_series_data',
            'remove_spatial_layer_data',
        ]
        for alg in self.algorithms:
            button = self.findChild(QPushButton, 'button_{0}'.format(alg))
            if not button:
                continue
            button.clicked.connect(partial(self.run_algorithm, alg))

        # Buttons not linked to algs
        #
        # Import observation data: need to dynamically instantiate the alg
        button = self.findChild(QPushButton, 'button_import_observation_data')
        if button:
            button.clicked.connect(self.run_import_observation_data)

        # Open online help
        button = self.findChild(QPushButton, 'button_online_help')
        if button:
            button.clicked.connect(self.on_line_help)

        # Connect on project load or new
        self.project = QgsProject.instance()
        self.iface.projectRead.connect(self.set_information_from_project)
        self.iface.newProjectCreated.connect(self.set_information_from_project)
        self.project.customVariablesChanged.connect(self.set_information_from_project)

        # Set information from project
        self.set_information_from_project()

    @staticmethod
    def check_database_version():
        """ Get the database G-Obs version"""
        # Query the database
        sql = '''
            SELECT me_version
            FROM gobs.metadata
            WHERE me_status = 1
            ORDER BY me_version_date DESC
            LIMIT 1;
        '''
        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')
        db_version = None
        if get_data == 'yes' and connection_name in get_postgis_connection_list():
            result, _ = fetch_data_from_sql_query(connection_name, sql)
            if result:
                for a in result:
                    db_version = a[0]
                    break

        return db_version

    def set_information_from_project(self):
        """ Set project based information such as database connection name """

        # Active connection
        connection_name = QgsExpressionContextUtils.projectScope(self.project).variable('gobs_connection_name')
        connection_stylesheet = 'padding: 3px;'
        connection_exists = False

        if connection_name:
            if connection_name in get_postgis_connection_list():
                connection_info = connection_name
                connection_stylesheet += "color: green;"
                connection_exists = True
            else:
                connection_info = tr(
                    'The connection "{}" does not exist'.format(connection_name)
                )
                connection_stylesheet += "color: red;"
        else:
            connection_info = tr(
                'No connection set for this project. '
                'Use the "Configure plugin" algorithm'
            )
            connection_stylesheet += "color: red;"

        # Check database version against plugin version
        plugin_version = version()
        self.plugin_version.setText(plugin_version)
        version_comment, version_stylesheet = self.check_database_status(connection_exists)

        self.version_comment.setText(version_comment)
        self.version_comment.setStyleSheet(version_stylesheet)

        # Set project connection name and stylesheet
        self.database_connection_name.setText(connection_info)
        self.database_connection_name.setStyleSheet(connection_stylesheet)

        # Toggle activation for buttons
        all_buttons = self.algorithms + [
            'import_observation_data',
        ]
        gobs_is_admin = QgsExpressionContextUtils.projectScope(self.project).variable('gobs_is_admin')
        for but in all_buttons:
            if but in ('configure_plugin', 'create_database_local_interface'):
                continue
            button = self.findChild(QPushButton, 'button_{0}'.format(but))
            if not button:
                continue
            button.setEnabled(connection_exists)

            # Disable and hide button if QGIS variable gobs_is_admin is not correctly set
            # We enable the structure button only if gobs_is_admin equals 'yes'
            if but not in ('create_database_structure', 'upgrade_database_structure'):
                continue
            button.setEnabled(connection_exists and gobs_is_admin == 'yes')
            if gobs_is_admin != 'yes':
                button.hide()
            else:
                button.show()

    def check_database_status(self, connection_exists) -> Tuple[str, str]:
        """ Compare the plugin version versus the database version. """
        # First check, if there isn't any connection set.
        if not connection_exists:
            version_comment = tr('Unknown database version')
            version_stylesheet = "font-weight: bold; color: orange;"
            return version_comment, version_stylesheet

        db_version = self.check_database_version()

        # Second check, if no metadata table has been found.
        if not db_version:
            version_comment = tr(
                'The database G-Obs version cannot be fetched from the given connection.'
            )
            version_stylesheet = "font-weight: bold; color: orange;"
            return version_comment, version_stylesheet

        self.database_version.setText(db_version)
        db_version_integer = format_version_integer(db_version)
        plugin_version_integer = format_version_integer(version())

        # Third check, if the database is in front of the plugin for their versions.
        if db_version_integer > plugin_version_integer:
            version_comment = tr(
                'The G-Obs plugin version is older than the database G-Obs version.'
                ' You need to upgrade your G-Obs QGIS plugin.'
            )
            version_stylesheet = "font-weight: bold; color: orange;"
            return version_comment, version_stylesheet

        has_migrations = len(available_migrations(plugin_version_integer)) >= 1
        # Fourth check, if there is a migration to run
        if has_migrations:
            # db_version_integer < plugin_version_integer
            version_comment = tr(
                'The database G-Obs version is older than your plugin version.'
                ' You need to run the algorithm "Upgrade database structure".'
            )
            version_stylesheet = "font-weight: bold; color: orange;"
            return version_comment, version_stylesheet

        # Finally, everything is alright
        version_comment = tr('The database is OK')
        version_stylesheet = "font-weight: bold; color: green;"
        return version_comment, version_stylesheet

    def run_algorithm(self, name):

        if name not in self.algorithms:
            self.iface.messageBar().pushMessage(
                tr("Error"),
                tr("This algorithm cannot be found") + ' {}'.format(name),
                level=Qgis.Critical
            )
            return

        # Run alg
        param = {}
        alg_name = 'gobs:{}'.format(name)
        execAlgorithmDialog(alg_name, param)
        if name in ('create_database_structure', 'upgrade_database_structure'):
            self.set_information_from_project()

    @staticmethod
    def get_series():
        # List of series
        sql = '''
            SELECT s.id,
            concat(
                id_label,
                ' (', p.pr_label, ')',
                ' / Source: ', a_label,
                ' / Layer: ', sl_label
            ) AS label
            FROM gobs.series s
            INNER JOIN gobs.protocol p ON p.id = s.fk_id_protocol
            INNER JOIN gobs.actor a ON a.id = s.fk_id_actor
            INNER JOIN gobs.indicator i ON i.id = s.fk_id_indicator
            INNER JOIN gobs.spatial_layer sl ON sl.id = s.fk_id_spatial_layer
            ORDER BY label
        '''
        project = QgsProject.instance()
        connection_name = QgsExpressionContextUtils.projectScope(project).variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')

        if get_data == 'yes' and connection_name in get_postgis_connection_list():
            result, _ = fetch_data_from_sql_query(connection_name, sql)
            return result

        return []

    def run_import_observation_data(self):

        # Get the list of series
        series = self.get_series()
        if not series:
            return

        # Create dialog to let the user choose the series
        dialog = QDialog()
        dialog.setWindowTitle(tr('Import observation data'))
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # Combobox
        combo_box = QComboBox()
        combo_box.setObjectName((tr('Choose series')))
        for i, d in enumerate(series):
            combo_box.addItem(d[1])
            combo_box.setItemData(i, d[0])
        layout.addWidget(combo_box)

        # Validation button
        button_box = QDialogButtonBox()
        button_box.addButton(QDialogButtonBox.Ok)
        button_box.button(QDialogButtonBox.Ok).clicked.connect(dialog.accept)
        layout.addWidget(button_box)

        if dialog.exec_() == QDialog.Accepted:
            idx = combo_box.currentIndex()
            val = combo_box.itemData(idx)
            self.open_import_observation_data(val)

    def open_import_observation_data(self, serie_id):
        """
        Opens the processing alg ImportObservationData
        with dynamic inputs based on given serie id
        """

        class DynamicImportObservationData(ImportObservationData):

            def name(self):
                return 'dynamic_import_observation_data'

            def displayName(self):
                return 'Import observation data'

            def group(self):
                return 'Manage'

            def groupId(self):
                return 'gobs_manage'

            def getSerieId(self):
                return serie_id

            def initAlgorithm(self, config):

                # use parent class to get other parameters
                super(self.__class__, self).initAlgorithm(config)

        alg = DynamicImportObservationData()
        alg.setProvider(QgsApplication.processingRegistry().providerById("gobs"))
        param = {}
        execAlgorithmDialog(alg, param)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    @staticmethod
    def open_external_resource(uri, is_url=True):
        """
        Opens a file with default system app
        """
        prefix = ''
        if not is_url:
            prefix = 'file://'
        webbrowser.open_new(r'{}{}'.format(prefix, uri))

    def on_line_help(self):
        """
        Display the help on concepts
        """
        url = 'https://docs.3liz.org/qgis-gobs-plugin/'
        self.open_external_resource(url)
