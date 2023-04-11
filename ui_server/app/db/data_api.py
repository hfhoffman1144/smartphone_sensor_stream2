import pandas as pd
import json
from ksql import KSQLAPI
from models.sensors import SensorName
from retry import retry
from typing import Generator, Callable

def maybe_load_json(x):
    
    try:

        return json.loads(x)
    
    except:

        return x

@retry()
async def ksql_sensor_push(client:KSQLAPI, sensor_name:SensorName, processing_func:Callable):

    """
    TODO
    """

    push_query = f'''
                  select deviceId,
                         time,
                         values_x,
                         values_y,
                         values_z
                    from device_stream
                    where name = '{sensor_name.value}'
                    emit changes
                   '''

    sensor_push_stream:Generator = client.query(push_query, use_http2=True)

    for row in sensor_push_stream:

        message = maybe_load_json(row)

        if type(message) == list:
            message[1] = str(pd.to_datetime(message[1]))
            await processing_func(message)
    