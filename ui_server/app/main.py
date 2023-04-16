import pandas as pd
import json
import logging
import sys
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from fastapi.requests import Request
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from core.config import app_config
from models.sensors import SensorName
from ksql import KSQLAPI
from db.data_api import ksql_sensor_push
import asyncio

KSQL_CLIENT = KSQLAPI('http://localhost:8088/')

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/chart-data/{client_id}")
async def message_stream(request: Request, client_id:str):
    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            
            yield {
                        "event": "new_message",
                        "id": "message_id",
                        "retry":1500000,
                        "data": f'yeah boi {client_id}'
                }

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
    