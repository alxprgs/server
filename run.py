import uvicorn
import asyncio
from server import logger
from server.core.config import settings

async def main():
    try:
        config = uvicorn.Config("server:app", port=int(settings.SERVER_PORT), host="0.0.0.0")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.critical("Ошибка при запуске: %s", e)

if __name__ == "__main__":
    asyncio.run(main())