import json
from fastapi import FastAPI
import asyncio
from aiokafka import AIOKafkaProducer
from schemas.sensors import SensorReading, SensorResponse
from core.config import app_config
from loguru import logger


# TODO: Move to separate file
def flatten_dict(nested_dict, parent_key='', sep='_'):
    """
    This function takes in a nested dictionary and returns a flattened dictionary.
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

app = FastAPI(title=app_config.PROJECT_NAME)

loop = asyncio.get_event_loop()

producer = AIOKafkaProducer(
    loop=loop,
    client_id=app_config.PROJECT_NAME,
    bootstrap_servers=app_config.KAFKA_URL
)

@app.on_event("startup")
async def startup_event():
    await producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()

@app.post("/phone-producer/")
async def kafka_produce(data: SensorReading):

    """
    Produce a message containing readings from a smartphone sensor.

    Parameters
    ----------
    data : SensorReading
        The request body containing sensor readings and metadata.

    Returns
    -------
    response : SensorResponse
        The response body corresponding to the processed sensor readings
        from the request.
    """

    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print(data.dict())
    print('########################################################')
    # Extract the messageId, deviceId, and sessionId
    message_info = data.dict().copy()
    message_info.pop('payload')

    # Write each individual sensor reading in the payload to kafka
    for sensor_reading in data.dict()['payload']:

        kafka_message = {**flatten_dict(sensor_reading), **message_info}
        await producer.send(app_config.TOPIC_NAME, json.dumps(kafka_message).encode("ascii"))

        #print(kafka_message)

    response = SensorResponse(
        messageId=data.messageId,
        sessionId=data.sessionId,
        deviceId=data.deviceId
    )

    logger.info(response)

    return response




