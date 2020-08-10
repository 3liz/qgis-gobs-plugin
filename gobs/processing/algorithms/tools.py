__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from gobs.qgis_plugin_tools.tools.i18n import tr
from qgis.core import QgsSettings
from processing.tools.postgis import uri_from_name


def getPostgisConnectionList():
    """Get a list of the PostGIS connection names"""

    s = QgsSettings()
    s.beginGroup("PostgreSQL/connections")
    connections = list(set([a.split('/')[0] for a in s.allKeys()]))
    s.endGroup()

    # In QGIS 3.16, we will use
    # metadata = QgsProviderRegistry.instance().providerMetadata('postgres')
    # find a connection by name
    # postgres_connections = metadata.connections()
    # connections = postgres_connections.keys()

    return connections


def getPostgisConnectionUriFromName(connection_name):
    """
    Return a QgsDatasourceUri from a PostgreSQL connection name
    """

    uri = uri_from_name(connection_name)

    # In QGIS 3.10, we will use
    # metadata = QgsProviderRegistry.instance().providerMetadata('postgres')
    # find a connection by name
    # connection = metadata.findConnection(connection_name)
    # uri_str = connection.uri()
    # uri = QgsDataSourceUri(uri)

    return uri


def fetchDataFromSqlQuery(connection_name, sql):

    from db_manager.db_plugins.plugin import BaseError
    from db_manager.db_plugins import createDbPlugin
    from db_manager.db_plugins.postgis.connector import PostGisDBConnector

    header = None
    data = []
    header = []
    rowCount = 0
    error_message = None
    connection = None

    # Create plugin class and try to connect
    ok = True
    try:
        dbpluginclass = createDbPlugin('postgis', connection_name)
        connection = dbpluginclass.connect()
    except BaseError as e:
        # DlgDbError.showError(e, self.dialog)
        ok = False
        error_message = e.msg
    except Exception:
        ok = False
        error_message = 'Cannot connect to database'

    if not connection:
        return [header, data, rowCount, ok, error_message]

    db = dbpluginclass.database()
    if not db:
        ok = False
        error_message = 'Unable to get database from connection'
        return [header, data, rowCount, ok, error_message]

    # Get URI
    uri = db.uri()
    try:
        connector = PostGisDBConnector(uri)
    except Exception:
        error_message = tr('Cannot connect to database')
        ok = False
        return [header, data, rowCount, ok, error_message]

    c = None
    ok = True
    # print "run query"
    try:
        c = connector._execute(None, str(sql))
        data = []
        header = connector._get_cursor_columns(c)
        if header is None:
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


def validateTimestamp(timestamp_text):
    from dateutil.parser import parse
    valid = True
    msg = ''
    try:
        parse(timestamp_text)
    except ValueError as e:
        valid = False
        msg = str(e)
    return valid, msg


def getVersionInteger(f):
    """
    Transform "0.1.2" into "000102"
    Transform "10.9.12" into "100912"
    to allow comparing versions
    and sorting the upgrade files
    """
    return ''.join([a.zfill(2) for a in f.strip().split('.')])
