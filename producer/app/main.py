import json
from fastapi import FastAPI
import asyncio
from aiokafka import AIOKafkaProducer
from schemas.sensors import SensorReading, SensorResponse
from core.config import app_config
from core.utils import flatten_dict
from loguru import logger


# Instantiate FastAPI app
app = FastAPI(title=app_config.PROJECT_NAME)

# Create the event loop
loop = asyncio.get_event_loop()

# Instatiate the Kafka producer object
producer = AIOKafkaProducer(
    loop=loop,
    client_id=app_config.PROJECT_NAME,
    bootstrap_servers=app_config.KAFKA_URL
)

@app.on_event("startup")
async def startup_event():
    
    await producer.start()
    await producer.send(app_config.TOPIC_NAME, json.dumps({'status':'ready'}).encode("ascii"))
    
@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()

@app.post("/phone-producer/")
async def kafka_produce(data: SensorReading):

    """
    Produce a message containing readings from a smartphone sensor to Kafka.

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
    
    # Extract the messageId, deviceId, and sessionId
    message_info = data.dict().copy()
    message_info.pop('payload')

    # Write each sensor reading in the payload to kafka
    for sensor_reading in data.dict()['payload']:

        print(sensor_reading)
        print('#####################################')
        kafka_message = {**flatten_dict(sensor_reading), **message_info}
        print(kafka_message)
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        await producer.send(app_config.TOPIC_NAME, json.dumps(kafka_message).encode("ascii"))

    response = SensorResponse(
        messageId=data.messageId,
        sessionId=data.sessionId,
        deviceId=data.deviceId
    )

    logger.info(response)

    return response




