import asyncio
import pandas as pd
import json
import logging
import sys
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from core.config import app_config
from models.sensors import SensorName
from ksql import KSQLAPI

KSQL_CLIENT = KSQLAPI('http://localhost:8088/')


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
origins = [
   f"http://localhost:{app_config.UI_PORT}",
   f"http://127.0.0.1:{app_config.UI_PORT}",
   f"http://0.0.0.0:{app_config.UI_PORT}"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory="templates")

def maybe_load_json(x):
    
    try:

        return json.loads(x)
    
    except:

        return x

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/chart-data')
async def message_stream(request: Request):
    def new_messages():
        yield True
    async def event_generator():
        while True:
           
            if await request.is_disconnected():
                break

            if new_messages():

                while True:
    
                    try:

                        recent_stream = KSQL_CLIENT.query('''
                            select deviceId,
                                time,
                                values_x,
                                values_y,
                                values_z
                            from device_stream
                            where name = 'accelerometeruncalibrated'
                            emit changes
                        ''', use_http2=True)

                        for row in recent_stream:

                            message_data = maybe_load_json(row)
                            if type(message_data) == list:

                                message_data[1] = str(pd.to_datetime(message_data[1]))

                                message = json.dumps(message_data)
                                yield {
                                        "event": "new_message",
                                        "id": "message_id",
                                        "retry":1500000,
                                        "data": message
                                }


                    except:

                        continue

    return EventSourceResponse(event_generator())