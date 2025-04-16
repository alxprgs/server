from server.core.functions.mongodb import check_auth, check_connection
from server.core.functions.hash import verify_hash
from server.core.functions.time import token_expiration_time
from server.core.api.schemes import AuthUser
from server import app, mongo, mongo_db, logger

from fastapi import Request, status
from fastapi.responses import JSONResponse

from secrets import token_urlsafe

@app.post("/user/auth_user", tags=["users"])
async def auth_user(data: AuthUser, request: Request):
    if await check_connection(mongo=mongo) == False:
        return JSONResponse({"status": False, "message": "Нет подключения к базе данных, действие невозможно."}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    auth = await check_auth(request=request, database=mongo_db)
    if auth:
        return JSONResponse({"status": False, "message": "Вы уже авторизированы."}, status_code=status.HTTP_409_CONFLICT)

    try:
        user = await mongo_db["users"].find_one({"login": data.login})
        if user:
            passwordpass = verify_hash(data.password, user["password"])
            if passwordpass == True:
                token = token_urlsafe(96)
                token_expiration = token_expiration_time()
                await mongo_db["users"].update_one({"login": data.login}, {"$set": {"token": token, "token_expiration": token_expiration}})
                
                response = JSONResponse({"status": True, "message": "Успешная авторизация."}, status_code=status.HTTP_200_OK)
                response.set_cookie("token", token, secure=True, httponly=True, samesite="Lax", max_age=3*24*60*60)
                return response
            else:
                return JSONResponse({"status": False, "message": "Неверный логин или пароль."}, status_code=status.HTTP_403_FORBIDDEN)
        else:
            return JSONResponse({"status": False, "message": "Неверный логин или пароль."}, status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.critical("Ошибка сервера: %s", e, exc_info=True)
        return JSONResponse({"status": False, "message": "Ошибка сервера."}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
