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

from PyQt5.QtCore import QCoreApplication
from qgis.core import (
    QgsDataSourceUri
)

def tr(string):
    return QCoreApplication.translate('Processing', string)

def getTableData(service, table, fields, orderColumn='id'):

    sql = 'SELECT "%s" FROM gobs."%s" ORDER BY "%s"' % (
        table,
        '", "'.join(fields),
        orderColumn
    )
    get_sql = self.run_sql(sql, service, None, None)
    ok = bool(get_sql['OUTPUT_STATUS'])
    msg = get_sql['OUTPUT_STRING']
    if not ok:
        return ok, msg
    msg = tr('Schema gobs does not exists. Continue...')
    data = []
    if 'OUTPUT_LAYER' in get_sql:
        for feature in get_sql['OUTPUT_LAYER'].getFeatures():
            line = {}
            for f in fields:
                line[f] = feature[f]
            data.append(
                line
            )
    return data


def fetchDataFromSqlQuery(service, sql):

    from db_manager.db_plugins.plugin import BaseError
    from db_manager.db_plugins.postgis.connector import PostGisDBConnector
    header = None
    data = []
    header = []
    rowCount = 0
    error_message = None

    uri = QgsDataSourceUri()
    uri.setConnection(service, '', '', '')
    try:
        connector = PostGisDBConnector(uri)
    except:
        error_message = tr('Cannot connect to database')
        ok = False
        return [header, data, rowCount, ok, error_message]

    c = None
    ok = True
    #print "run query"
    try:
        c = connector._execute(None,str(sql))
        data = []
        header = connector._get_cursor_columns(c)
        if header == None:
            header = []
        if len(header) > 0:
            data = connector._fetchall(c)
        rowCount = c.rowcount
        if rowCount == -1:
            rowCount = len(data)

    except BaseError as e:
        ok = False
        error_message = e.msg
        return [header, data, rowCount, ok, error_message]
    finally:
        if c:
            c.close()
            del c

    # Log errors
    if not ok:
        error_message = tr('Unknown error occured while fetching data')
        return [header, data, rowCount, ok, error_message]
        print(error_message)
        print(sql)

    return [header, data, rowCount, ok, error_message]


