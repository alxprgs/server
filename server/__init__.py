import os
import logging
import colorlog
import torch
import asyncio

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from functions import DatabaseOperations
from fastapi import FastAPI
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles

log_format = "%(log_color)s%(levelname)s:%(reset)s     %(message)s"
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

eth_mode = None
load_dotenv()
client = AsyncIOMotorClient(os.getenv("MONGO_URL"), serverSelectionTimeoutMS=1000, socketTimeoutMS=1000)
database = client["ASFES"]
eth_mode = True

try:
    asyncio.run(DatabaseOperations.system_log(t="Successful connection to database"))
    eth_mode = True
except Exception as e:
    eth_mode = False

app_title = "ASFES | SERVER API"
if not eth_mode:
    app_title = "ASFES | SERVER API (NONE DB CONNECTION)"

app = FastAPI(
    title=app_title,
    version="Dev 6.0.1 | Build 18.12.2024",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.mount("/static", StaticFiles(directory="server/static"))
model = torch.hub.load('ultralytics/yolov5', 'custom', path='server/models/best.pt')

@app.on_event("startup")
async def startup_event():
    if eth_mode == False:
        logging.critical(f"Connection error to database, set offline mode.")
    else:
        logging.info(f"Successful connection to database.")

security = HTTPBasic()

from server.routes.user import auth_user, check_auth, create_user, leave_user, set_permission
from server.routes.development import docs, clear, server_status
from server.routes.smm import send_mail
from server.routes.device import add_device
from server.routes.processing import find_Fire
