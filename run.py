import uvicorn
from functions import clear
from server import client, logging

if __name__ == "__main__":
    try:
        clear()
        uvicorn.run("server:app", port=5005, host="0.0.0.0",reload= True)
    except Exception as e:
        logging.critical(f"error: {e}")
    finally:
        client.close()
        logging.info("Connection close.")