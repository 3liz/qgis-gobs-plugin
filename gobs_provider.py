# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Gobs
                                 A QGIS plugin
 This plugin provides tools to store and manage spatial and time data in a standardized way
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-02-15
        copyright            : (C) 2019 by 3liz
        email                : info@3liz.com
 ***************************************************************************/

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

from qgis.core import QgsProcessingProvider
from .gobs_execute_sql_on_service_algorithm import GobsExecuteSqlOnServiceAlgorithm


class GobsProvider(QgsProcessingProvider):

    def __init__(self):
        QgsProcessingProvider.__init__(self)

        # Load algorithms
        self.alglist = [
            GobsExecuteSqlOnServiceAlgorithm()
        ]

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        for alg in self.alglist:
            self.addAlgorithm( alg )

    def id(self):
        return 'Gobs'

    def name(self):
        return self.tr('G-Obs')

    def longName(self):
        return self.tr('G-Obs')
