import uvicorn
import asyncio
from functions import SystemUtils, Setup
from server import client, logging

async def main():
    try:
        SystemUtils.clear()
        await Setup.root_user()
        config = uvicorn.Config("server:app", port=5005, host="0.0.0.0")
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logging.critical(f"error: {e}")
    finally:
        client.close()
        logging.info("Connection to database closed.")

if __name__ == "__main__":
    asyncio.run(main())