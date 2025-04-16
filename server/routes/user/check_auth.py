from server import app, mongo_db, mongo
from server.core.functions.mongodb import check_auth, check_connection
from fastapi import Request, status
from fastapi.responses import JSONResponse

@app.get("/user/check_auth", tags=["users"])
async def check_auth_s(request: Request):
    if await check_connection(mongo=mongo) == False:
        return JSONResponse({"status": False, "message": "Нет подключения к базе данных, действие невозможно."}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return await check_auth(request=request, database=mongo_db)