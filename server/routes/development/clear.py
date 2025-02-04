from server import app
from functions import SystemUtils
from fastapi.responses import PlainTextResponse

@app.post("/dev/clear", tags=["development"], response_class=PlainTextResponse)
async def clear_cmd():
    try:
        SystemUtils.clear()
        return True
    except Exception as e:
        return e
