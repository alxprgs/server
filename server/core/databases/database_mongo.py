from motor.motor_asyncio import AsyncIOMotorClient
from server import logger
from server.core.config import settings

async def connect_mongo():
    try:
        client = AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
        try:
            await client.admin.command("ping")
        except Exception as e:
            logger.critical("Ошибка подключения к MongoDB: %s", e, exc_info=True)
            return False, None, None
        database = client["ASFES"]
        logger.info("Успешное подключение к MongoDB.")
        return True, database, client
    except Exception as e:
        logger.critical("Ошибка подключения к MongoDB: %s", e, exc_info=True)
        return False, None, None
