from functions import check_auth, create_hash, generate_random_word, create_random
from server import app, database

from fastapi import Request
from fastapi.responses import JSONResponse

from secrets import token_urlsafe

@app.get("/user/auth_user")
async def auth_user(login, password, request: Request):
    auth = await check_auth(request=request)
    if auth == True:
        return JSONResponse({"status": False, "message": "Вы уже авторизированы."}, status_code=400)
    else:
        user = await database["users"].find_one({"login": login})
        if user:
            password = await create_hash(text=password)
            if password == user["password"]:
                tokens = {await generate_random_word(15): token_urlsafe(64) for _ in range(5)}
                await database["users"].find_one_and_update({"login": login},{"$set": {"tokens": tokens}})
                response = JSONResponse({"status": True, "message": "Успешная авторизация."}, status_code=200)
                for key, value in tokens.items():
                    response.set_cookie(key, value)
                response.set_cookie("login", login)
                response = await create_random(response=response)
                return response
            else:
                return JSONResponse({"status": False, "message": "Неверный пароль."}, status_code=403)
        else:
            return JSONResponse({"status": False, "message": "Пользовател не найден."}, status_code=400)
            
