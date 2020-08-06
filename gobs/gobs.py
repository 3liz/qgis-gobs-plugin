__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

import inspect
import os
import sys

from qgis.PyQt.QtCore import (
    Qt,
    QTranslator,
    QCoreApplication,
)
from qgis.core import (
    QgsApplication,
    QgsSettings,
)

from gobs.qgis_plugin_tools.tools.resources import resources_path
from .gobs_dockwidget import GobsDockWidget
from .processing.provider import GobsProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class GobsPlugin(object):

    def __init__(self, iface):
        self.provider = None
        self.dock = None
        self.iface = iface

        try:
            locale = QgsSettings().value('locale/userLocale', 'en')[0:2]
        except AttributeError:
            locale = 'en'
        locale_path = resources_path('i18n', '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

    def initProcessing(self):
        """Load the Processing provider. QGIS 3.8."""
        self.provider = GobsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()
        self.dock = GobsDockWidget(self.iface)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)

    def unload(self):
        if self.dock:
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)
