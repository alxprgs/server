import uvicorn
from functions import SystemUtils
from server import client, logging

if __name__ == "__main__":
    try:
        SystemUtils.clear()
        uvicorn.run("server:app", port=5005, host="0.0.0.0")
    except Exception as e:
        logging.critical(f"error: {e}")
    finally:
        client.close()
        logging.info("Connection to database close.")