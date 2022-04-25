__copyright__ = "Copyright 2020, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"
__revision__ = "$Format:%H$"

from typing import Any, List, Tuple, Union

from qgis.core import (
    QgsDataSourceUri,
    QgsProviderConnectionException,
    QgsProviderRegistry,
)

from gobs.qgis_plugin_tools.tools.resources import plugin_path


def get_postgis_connection_list():
    """Get a list of the PostGIS connection names"""
    metadata = QgsProviderRegistry.instance().providerMetadata('postgres')
    postgres_connections = metadata.connections()
    connections = postgres_connections.keys()
    return connections


def get_postgis_connection_uri_from_name(connection_name: str) -> QgsDataSourceUri:
    """
    Return a QgsDatasourceUri from a PostgreSQL connection name
    """
    metadata = QgsProviderRegistry.instance().providerMetadata('postgres')
    connection = metadata.findConnection(connection_name)
    return QgsDataSourceUri(connection.uri())


def fetch_data_from_sql_query(connection_name: str, sql: str) -> Union[Tuple[Any, None], Tuple[List[Any], str]]:
    """Execute SQL and return the result."""
    metadata = QgsProviderRegistry.instance().providerMetadata('postgres')
    connection = metadata.findConnection(connection_name)

    try:
        result = connection.executeSql(sql)
        return result, None
    except QgsProviderConnectionException as e:
        return [], str(e)


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


def createAdministrationProjectFromTemplate(connection_name, project_file_path):
    """
    Creates a new administration project from template
    for the given connection name
    to the given target path
    """
    # Get connection information
    uri = get_postgis_connection_uri_from_name(connection_name)
    connection_info = uri.connectionInfo()

    # Read in the template file
    template_file = plugin_path('resources', 'qgis', 'gobs_administration.qgs')
    with open(template_file, 'r') as fin:
        filedata = fin.read()

    # Replace the database connection information
    filedata = filedata.replace(
        "service='gobs'",
        connection_info
    )

    # Replace also the QGIS project variable
    filedata = filedata.replace(
        "gobs_connection_name_value",
        connection_name
    )
    with open(project_file_path, 'w') as fout:
        fout.write(filedata)
