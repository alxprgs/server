import os
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from functions import system_log
from fastapi import FastAPI
from fastapi.security import HTTPBasic


load_dotenv()

try:
    client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
    database = client["ASFES"]
except Exception as e:
    print(f"Connection error: {e}")
    sys.exit(0)

app = FastAPI(
    title="ASFES | SERVER API",
    version="Dev 2.6 | Build 09.12.2024",
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
        print("Successful connection")
    except Exception as e:
        print(f"Error in system log: {e}")

security = HTTPBasic()

from server.routes.user import auth_user, check_auth, create_user, leave_user, set_permission
from server.routes.development import docs, clear
