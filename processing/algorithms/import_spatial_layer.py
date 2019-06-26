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

class ImportSpatialLayer(QgsProcessingAlgorithm):
    """
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    PGSERVICE = 'PGSERVICE'
    LAYER = 'LAYER'
    UNIQUEID = 'UNIQUEID'
    UNIQUELABEL = 'UNIQUELABEL'
    ACTOR = 'ACTOR'
    GEOMETRYTYPE = 'GEOMETRYTYPE'

    OUTPUT_STATUS = 'OUTPUT_STATUS'
    OUTPUT_STRING = 'OUTPUT_STRING'

    def name(self):
        return 'gobs_import_spatial_layer'

    def displayName(self):
        return self.tr('Import spatial layer')

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
        self.addParameter(
            QgsProcessingParameterString(
                self.PGSERVICE,
                'PostgreSQL Service',
                defaultValue='gobs',
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.LAYER,
                self.tr('Source data layer'),
                optional=False
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUEID,
                self.tr('Unique identifier'),
                parentLayerParameterName=self.LAYER
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.UNIQUELABEL,
                self.tr('Unique label'),
                parentLayerParameterName=self.LAYER,
                type=QgsProcessingParameterField.String
            )
        )
        actors = ['NONE', 'IGN', 'CIRAD']
        self.addParameter(
            QgsProcessingParameterEnum(
                self.ACTOR, self.tr('Source actor'),
                options=actors,
                optional=False
            )
        )

        geometrytypes = [
            'Point', 'MultiPoint',
            'Linestring', 'MultiLinestring',
            'Polygon', 'MultiPolygon'
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.GEOMETRYTYPE, self.tr('Geometry type'),
                options=geometrytypes,
                optional=False
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
        service = parameters[self.PGSERVICE]
        layer = self.parameterAsVectorLayer(parameters, self.LAYER, context)
        uniqueid = self.parameterAsString(parameters, self.UNIQUEID, context)
        uniquelabel = self.parameterAsString(parameters, self.UNIQUELABEL, context)

        msg = ''
        status = 1

        # Loop throug features
        for feat in layer.getFeatures():
            feedback.pushInfo(
                'ID = %s - LABEL = %s' % (
                    feat[uniqueid],
                    feat[uniquelabel]
                )
            )

        msg = self.tr('Spatial data objects have been imported')

        return {
            self.OUTPUT_STATUS: status,
            self.OUTPUT_STRING: msg
        }
