from server import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from server.core.config import settings
from dotenv import load_dotenv

async def connect_mysql():
    load_dotenv(override=True)
    if settings.MYSQL_URL == None:
        logger.critical("Ошибка подключения к mysql, отсутсвует HOST")
        return False, None
    engine = create_async_engine(settings.MYSQL_URL)
    try:
        async with engine.connect() as mysql_db:
            result = await mysql_db.execute(text("SELECT 1"))
            if result:
                logger.info("Успешное подключение к MySql.")
                return True, engine
            return False, None
    except Exception as e:
        logger.critical("Ошибка подключения к MySQL: %s", str(e), exc_info=True)
        await engine.dispose()
        return False, None