from server import app, eth_mode
from functions import SystemMetrics

from fastapi.responses import JSONResponse

@app.get("/dev/server_status")
async def server_status():
    try:
        response = JSONResponse({
            "ram load": await SystemMetrics.get_ram_load(),
            "cpu load": await SystemMetrics.get_cpu_load(),
            "database_status": eth_mode
            }, status_code=200)
    except Exception as e:
        response = JSONResponse({"status": False, "message": f"server error: {e}"}, status_code=500)
    return response