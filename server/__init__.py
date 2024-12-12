import os
import signal
import logging
import colorlog

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from functions import system_log
from fastapi import FastAPI
from fastapi.security import HTTPBasic

LOG_FORMAT = "%(log_color)s%(levelname)s:%(reset)s     %(message)s"
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(LOG_FORMAT))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
load_dotenv()

try:
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    database = client["ASFES"]
except Exception as e:
    logging.critical(f"Connection error to database: {e}")
    os.kill(os.getpid(), signal.SIGINT)

app = FastAPI(
    title="ASFES | SERVER API",
    version="Dev 5.0.0 | Build 13.12.2024",
    contact={
        "name": "Александр",
        "email": "aleksahalaya@yandex.ru"},
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

@app.on_event("startup")
async def startup_event():
    try:
        await system_log(t="Successful connection to database")
        logging.info("Successful connection to database")
    except Exception as e:
        logging.error(f"Error in system log: {e}")

security = HTTPBasic()

from server.routes.user import auth_user, check_auth, create_user, leave_user, set_permission
from server.routes.development import docs, clear, server_status
from server.routes.smm import send_mail
from server.routes.device import add_device
