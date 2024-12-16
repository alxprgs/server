from server import app
from functions import SystemUtils

@app.get("/dev/clear")
async def clear_cmd():
    try:
        SystemUtils.clear()
        return True
    except Exception as e:
        return e
