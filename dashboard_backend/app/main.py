import pandas as pd
import json
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from fastapi.requests import Request
from starlette.middleware.cors import CORSMiddleware
from core.config import app_config
from core.utils import maybe_load_json
from models.sensors import SensorName
from db.data_api import (create_ksql_connection,
                         create_ksql_device_stream,
                         ksql_sensor_push)


# Instantiate KSQLAPI object
KSQL_CLIENT = create_ksql_connection(app_config.KSQL_URL)

# Create the KSQL device stream if it doesn't exist
create_ksql_device_stream(
    KSQL_CLIENT, app_config.STREAM_NAME, app_config.TOPIC_NAME)

# Instantiate FastAPI app
app = FastAPI()

# Configure middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# An SSE endpoint that pushes sensor data from KSQLDB to the client


@app.get("/chart-data/{client_id}")
async def message_stream(request: Request, client_id: str):
    async def event_generator():
        while True:
            # If the client closes the connection, stop sending events
            if await request.is_disconnected():
                break

            try:

                # Get the KSQL stream generator
                sensor_push_stream = ksql_sensor_push(
                    KSQL_CLIENT, app_config.STREAM_NAME, SensorName.ACC)

                for raw_message in sensor_push_stream:

                    # If client closes connection, stop sending events
                    if await request.is_disconnected():
                        break

                    # Check if the raw message is the correct format
                    message = maybe_load_json(raw_message)

                    print(message)

                    # If the message is in the correct format, send to client
                    if isinstance(message, list):

                        message[1] = str(pd.to_datetime(message[1]))
                        yield {
                            "event": "new_message",
                            "id": "message_id",
                            "retry": 1500000,
                            "data": json.dumps(message)
                        }
            except Exception as e:

                if await request.is_disconnected():

                    break

                continue

    return EventSourceResponse(event_generator())
