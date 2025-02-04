import os
import logging
import colorlog
import torch
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from fastapi import FastAPI
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from functions import DatabaseOperations

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
        "description": "Инструменты для разработки."
    },
    {
        "name": "smm",
        "description": "Взаимодействие пользователями."
    },
    {
        "name": "processing",
        "description": "Обработка."
    },
    {
        "name": "redirect",
        "description": "Авторизация через сторонние приложения."
    }
]

app_title = "ASFES | SERVER API"
if not eth_mode:
    app_title = "ASFES | SERVER API (NONE DB CONNECTION)"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global eth_mode
    try:
        await client.admin.command('ping')
        await DatabaseOperations.system_log(t="Успешное подключение к базе данных.")
        eth_mode = True
    except Exception as e:
        logger.critical(f"Ошибка подключения к базе данных: {e}")
        eth_mode = False
    yield

app = FastAPI(
    title=app_title,
    version="Stable 10.0.0 | Build 05.02.2025",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

app.mount("/html/static", StaticFiles(directory="server/static"))
model = None
templates = Jinja2Templates(directory="server/static")


security = HTTPBasic()

from server.routes.user import auth_user, check_auth, create_user, leave_user, set_permission, del_user
from server.routes.development import docs, clear, server_status
from server.routes.smm import send_mail
from server.routes.device import add_device
from server.routes.processing import find_firev3
from server.routes.html import auth, root, error404
from server.routes.redirect import yandex, vk