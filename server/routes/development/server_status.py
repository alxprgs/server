from server import app
from functions import get_cpu_load, get_ram_load

from fastapi.responses import JSONResponse

@app.get("/dev/server_status")
async def server_status():
    try:
        response = JSONResponse({
            "ram load": await get_ram_load(),
            "cpu load": await get_cpu_load()
            }, status_code=200)
    except Exception as e:
        response = JSONResponse({"status": False, "message": f"server error: {e}"}, status_code=500)
    return response