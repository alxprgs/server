from server import app
from functions import SystemUtils

@app.post("/dev/clear", tags=["development"])
async def clear_cmd():
    try:
        SystemUtils.clear()
        return True
    except Exception as e:
        return e
