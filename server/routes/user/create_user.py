from server import app, database
from secrets import token_urlsafe
from functions import RandomUtils, HashUtils
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import EmailStr


@app.post("/user/create_user", tags=["users"])
async def create_user(login: str, password: str, mail: EmailStr):
    db = database["users"]
    try:
        if await db.find_one({"login": login}):
            return JSONResponse({"status": False, "message": "Пользователь с таким логином уже зарегистрирован."}, status_code=400)

        if await db.find_one({"mail": mail}):
            return JSONResponse({"status": False, "message": "Пользователь с такой почтой уже зарегистрирован."}, status_code=400)

        hashed_password = await HashUtils.create_hash(text=password)
        tokens = {await RandomUtils.generate_random_word(15): token_urlsafe(64) for _ in range(5)}

        await db.insert_one({
            "login": login,
            "mail": mail,
            "password": hashed_password,
            "tokens": tokens,
            "permissions": {
                "user": True,
                "administrator": False,
                "Developer": False
            },
            "auth_type": "password"
        })

        response = JSONResponse({"status": True, "message": "Успешная регистрация."}, status_code=200)
        response.set_cookie("login", login)
        for key, value in tokens.items():
            response.set_cookie(key, value)
        response = await RandomUtils.create_random(response=response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {e}")
