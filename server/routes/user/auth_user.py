from server import app, database
from fastapi import Request
from fastapi.responses import JSONResponse
from functions import check_auth, create_hash
from secrets import token_urlsafe

@app.get("/user/login_user")
async def login_user(login, password, request: Request):
    auth = await check_auth(request=request)
    if auth == True:
        return JSONResponse({"status": False, "message": "Вы уже авторизированы."})
    else:
        user = await database["users"].find_one({"login": login})
        if user:
            password = await create_hash(text=password)
            if password == user["password"]:
                token = token_urlsafe(256)
                await database["users"].find_one_and_update({"login": login},{"$set": {"token": token}})
                response = JSONResponse({"status": True, "message": "Успешная авторизация."})
                response.set_cookie(key="token", value=token)
                return response
            else:
                return JSONResponse({"status": False, "message": "Неверный пароль."})
        else:
            return JSONResponse({"status": False, "message": "Пользовател не найден."})
            
