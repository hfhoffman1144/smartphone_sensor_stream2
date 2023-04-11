import pandas as pd
import json
import logging
import sys
from fastapi import FastAPI, WebSocket
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.config import app_config
from models.sensors import SensorName
from ksql import KSQLAPI
from db.data_api import ksql_sensor_push

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
    
@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/chart-data")
async def chart_data_endpoint(websocket: WebSocket):

    await websocket.accept()

    while True:
        
        try:
            await ksql_sensor_push(KSQL_CLIENT, SensorName.ACC, websocket.send_json)
        except:
            continue