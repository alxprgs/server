from server import app, eth_mode
from functions import DatabaseOperations

from fastapi import Request
from fastapi.responses import JSONResponse

@app.post("/user/check_auth", tags=["users"])
async def check_auth_s(request: Request):
    if eth_mode == False:
        return JSONResponse({"status": False, "message": "Отсутствует доступ к базе данных. Взаимодействие невозможно."}, status_code=523)
    return await DatabaseOperations.check_auth(request=request)