from retry import retry
from ksql import KSQLAPI
from models.sensors import SensorName
from typing import Generator


@retry()
def create_ksql_connection(url: str) -> KSQLAPI:
    """
    Create a connection to a KSQL server using the provided URL.

    Parameters
    ----------
    url : str
        The URL of the KSQL server to connect to.

    Returns
    -------
    KSQLAPI
        An instance of the `KSQLAPI` class representing the connection to the KSQL server.
    """

    return KSQLAPI(url)


def create_ksql_device_stream(client: KSQLAPI,
                              stream_name: str,
                              topic_name: str) -> None:
    """
    Creates a new device stream in KSQL server if it does not already exist.

    Parameters:
    -----------
    client : KSQLAPI
        A client instance of the KSQLAPI class to connect with KSQL server.
    stream_name : str
        The name of the device stream to create.
    topic_name : str
        The name of the Kafka topic to associate with the device stream.

    Returns:
    --------
    None

    Raises:
    -------
    KSQLServerError
        If there is an error while creating the stream in KSQL server.
    """

    # Get the current streams
    curr_streams = client.ksql('show streams')
    curr_stream_names = [stream['name'].lower()
                         for stream in curr_streams[0]['streams']]

    # If the device stream doesn't exist, create it
    if stream_name.lower() not in curr_stream_names:

        client.create_stream(table_name=stream_name,
                             columns_type=['name varchar',
                                           'time bigint',
                                           'values_x double',
                                           'values_y double',
                                           'values_z double',
                                           'messageId bigint',
                                           'sessionId varchar',
                                           'deviceId varchar'
                                           ],
                             topic=topic_name,
                             value_format='JSON')


def ksql_sensor_push(client: KSQLAPI,
                     stream_name: str,
                     sensor_name: SensorName) -> Generator:
    """
    Generator function that continuously pushes sensor data
    for a given sensor name from a KSQL server using the KSQL API client.

    Parameters:
    -----------
    client : KSQLAPI
        The KSQL API client instance used to query the KSQL server.
    stream_name : str
        The name of the KSQL stream to query data from.
    sensor_name : SensorName
        An enum value representing the name of the sensor to stream data for.

    Returns:
    --------
    Generator:
        A generator object that yields the sensor data as it is streamed in real-time.
    """

    push_query = f'''
                  select deviceId,
                         time,
                         values_x,
                         values_y,
                         values_z
                    from {stream_name}
                    where name = '{sensor_name.value}'
                    emit changes
                   '''

    sensor_push_stream: Generator = client.query(push_query, use_http2=True)

    return sensor_push_stream
