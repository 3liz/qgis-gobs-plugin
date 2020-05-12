__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from functools import partial

from qgis.PyQt import (
    QtWidgets,
)
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import (
    QPushButton,
    QComboBox,
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
)
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsExpressionContextUtils,
)

from processing import execAlgorithmDialog

from .processing.algorithms.import_observation_data import ImportObservationData
from .processing.algorithms.tools import fetchDataFromSqlQuery
from db_manager.db_plugins import createDbPlugin

from gobs.qgis_plugin_tools.tools.i18n import tr
from gobs.qgis_plugin_tools.tools.resources import load_ui, plugin_path

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

            'import_spatial_layer_data',

            'get_spatial_layer_vector_data',
            'get_series_data',
            'get_series_list',
            'get_aggregated_data',
        ]
        for alg in self.algorithms:
            button = self.findChild(QPushButton, 'button_{0}'.format(alg))
            if not button:
                continue
            button.clicked.connect(partial(self.runAlgorithm, alg))

        # Buttons not linked to algs
        #
        # Import observation data: need to dynamically instantiate the alg
        button = self.findChild(QPushButton, 'button_import_observation_data')
        if button:
            button.clicked.connect(self.runImportObservationData)

        # Help on concepts
        button = self.findChild(QPushButton, 'button_help_concept')
        if button:
            button.clicked.connect(self.helpConcept)

        # Help on database
        button = self.findChild(QPushButton, 'button_help_database')
        if button:
            button.clicked.connect(self.helpDatabase)

    def runAlgorithm(self, name):

        if name not in self.algorithms:
            self.iface.messageBar().pushMessage(
                tr("Error"),
                tr("This algorithm cannot be found") + ' {}'.format(name),
                level=Qgis.Critical
            )
            return

        # Run alg
        param = {}
        alg_name = 'gobs:{0}'.format(name)
        execAlgorithmDialog(alg_name, param)

    @staticmethod
    def getSeries():
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
        connection_name = QgsExpressionContextUtils.globalScope().variable('gobs_connection_name')
        get_data = QgsExpressionContextUtils.globalScope().variable('gobs_get_database_data')
        dbpluginclass = createDbPlugin('postgis')
        connections = [c.connectionName() for c in dbpluginclass.connections()]
        series = []
        if get_data == 'yes' and connection_name in connections:
            [header, data, rowCount, ok, error_message] = fetchDataFromSqlQuery(
                connection_name,
                sql
            )
            series = data

        return series

    def runImportObservationData(self):

        # Get the list of series
        series = self.getSeries()
        if not series:
            return

        # Create dialog to let the user choose the serie
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
            self.openImportObservationData(val)

    def openImportObservationData(self, serie_id):
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
    def openFile(file_path):
        """
        Opens a file with default system app
        """
        import webbrowser
        webbrowser.open_new(r'file://%s' % file_path)

    def helpConcept(self):
        """
        Display the help on concepts
        """
        help_file = plugin_path('doc', 'concepts.md')
        self.openFile(help_file)

    def helpDatabase(self):
        """
        Display the help on database structure
        """
        help_file = plugin_path(
            'doc', 'database', 'schemaspy', 'html', 'gobs',
            'diagrams', 'summary', 'relationships.real.large.png'
        )
        self.openFile(help_file)
