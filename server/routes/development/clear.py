from server import app
from functions import clear

@app.get("/dev/clear")
async def clear_cmd():
    try:
        clear()
        return True
    except Exception as e:
        return e
