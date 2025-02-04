from functions import DatabaseOperations, HashUtils, RandomUtils
from server import app, database

from fastapi import Request
from fastapi.responses import JSONResponse

from secrets import token_urlsafe

@app.post("/user/auth_user", tags=["users"])
async def auth_user(request: Request, login: str , password: str,):
    auth = await DatabaseOperations.check_auth(request=request)
    if auth:
        return JSONResponse({"status": False, "message": "Вы уже авторизированы."}, status_code=400)

    try:
        user = await database["users"].find_one({"login": login})
        if user:
            hashed_password = await HashUtils.create_hash(text=password)
            if hashed_password == user["password"]:
                tokens = {await RandomUtils.generate_random_word(15): token_urlsafe(64) for _ in range(5)}
                await database["users"].update_one({"login": login}, {"$set": {"tokens": tokens}})
                
                response = JSONResponse({"status": True, "message": "Успешная авторизация."}, status_code=200)
                for key, value in tokens.items():
                    response.set_cookie(key, value, secure=True, httponly=True)
                response.set_cookie("login", login, secure=True, httponly=True)
                
                response = await RandomUtils.create_random(response=response)
                return response
            else:
                return JSONResponse({"status": False, "message": "Неверный пароль."}, status_code=403)
        else:
            return JSONResponse({"status": False, "message": "Пользователь не найден."}, status_code=404)
    except Exception as e:
        return JSONResponse({"status": False, "message": f"error: {str(e)}"}, status_code=500)
