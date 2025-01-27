import os
import logging
import colorlog
import torch

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi import FastAPI
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

log_format = "%(log_color)s%(levelname)s:%(reset)s     %(message)s"
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

eth_mode = None
load_dotenv()
client = AsyncIOMotorClient(os.getenv("MONGO_URL"), serverSelectionTimeoutMS=5000, socketTimeoutMS=5000)
database = client["ASFES"]
eth_mode = True

tags_metadata = [
    {
        "name": "users",
        "description": "Взаимодействие с аккаунтом в базе данных и на стороне клиента."
    },
    {
        "name": "html",
        "description": "Получение страниц html."
    },
    {
        "name": "device",
        "description": "Взаимодействие с установками пожаротушения."
    },
    {
        "name": "development",
    },
    {
        "name": "smm",
        "description": "Взаимодействие пользователями."
    },
    {
        "name": "processing",
        "description": "Обработка."
    },
]

app_title = "ASFES | SERVER API"
if not eth_mode:
    app_title = "ASFES | SERVER API (NONE DB CONNECTION)"

app = FastAPI(
    title=app_title,
    version="Stable 9.0.0 | Build 27.01.2025",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    openapi_tags=tags_metadata
)

app.mount("/html/static", StaticFiles(directory="server/static"))
model = None
try:
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='server/models/best.pt', force_reload=True)
except Exception as e:
    logger.error(f"Failed to load YOLOv5 model: {str(e)}")
templates = Jinja2Templates(directory="server/static")


security = HTTPBasic()

from server.routes.user import auth_user, check_auth, create_user, leave_user, set_permission, del_user
from server.routes.development import docs, clear, server_status
from server.routes.smm import send_mail
from server.routes.device import add_device
from server.routes.processing import find_fire, find_firev2, find_firev3
from server.routes.html import auth, root
from server.routes.redirect import yandex, vk
