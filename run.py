import uvicorn
from functions import clear
from server import app, client
from dotenv import load_dotenv

if __name__ == "__main__":
    try:
        clear()
        uvicorn.run("server:app", port=5005, host="0.0.0.0")
    except Exception as e:
        print(f"error: {e}")
    finally:
        client.close()