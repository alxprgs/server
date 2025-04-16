from redis.asyncio import Redis
from server import logger
from server.core.config import settings

from dotenv import load_dotenv

async def connect_redis():
    load_dotenv(override=True)
    if settings.REDIS_HOST == None:
        logger.critical("Ошибка подключения к redis, отсутсвует HOST")
        return False, None

    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=int(settings.REDIS_PORT),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )

    try:
        if await redis_client.ping():
            logger.info("Успешное подключение к Redis.")
            return True, redis_client
    except Exception as e:
        logger.critical("Ошибка подключения к redis: %s", e, exc_info=True)
        return False, None
